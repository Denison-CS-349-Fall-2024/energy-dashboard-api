import re
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime

import pandas as pd
from fuzzywuzzy import fuzz, process

from app.config import settings
from app.schemas import ChartType, QuickInsightsType

TIME_UNIT_MAPPING = {"All": "YEAR", "Y": "MONTH", "M": "DAY", "D": "HOUR"}
NAME_SIMILARITY_THRESHOLD = 80


def convert_unix_time_to_datetime_string(unix_time: int, only_need_date=False):
    timestamp_sec = int(unix_time) / 1000
    date = datetime.fromtimestamp(timestamp_sec)
    formatted_date = (
        date.strftime("%Y-%m-%d")
        if only_need_date
        else date.strftime("%Y-%m-%d %H:%M:%S")
    )
    return formatted_date


def convert_year_to_datetime_string(year):
    date = datetime(year, 1, 1)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def get_energy_unit_from_raw(energy_unit_string: str):
    match = re.search(r"\((.*?)\)", energy_unit_string)
    if match:
        return match.group(1).strip()  # Strip any surrounding whitespace

    return ""


def infer_start_and_end_date_from_chart_type_and_chart_date(
    chart_type: ChartType, chart_date: date
):

    if chart_type == ChartType.Y:
        start_date = datetime(chart_date.year, 1, 1)  # Start of the year
        end_date = datetime(chart_date.year, 12, 31)  # End of the year

    elif chart_type == ChartType.M:
        start_date = datetime(
            chart_date.year, chart_date.month, 1
        )  # Start of the month
        last_day = monthrange(chart_date.year, chart_date.month)[
            1
        ]  # Get the last day of the month
        end_date = datetime(
            chart_date.year, chart_date.month, last_day
        )  # End of the month

    elif chart_type == ChartType.D:
        start_date = datetime(
            chart_date.year, chart_date.month, chart_date.day
        )  # Start of the day
        end_date = datetime(
            chart_date.year, chart_date.month, chart_date.day
        )  # End of the day

    elif chart_type == ChartType.All:
        start_date = datetime.strptime("2000-01-01", "%Y-%m-%d")  # Start of All
        end_date = datetime.today().date()  # End of All

    # Format the start and end dates as strings
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    return start_date_str, end_date_str


def infer_quick_insights_from_solar_edge_data(site_details, site_overview):
    installed_on = site_details["details"]["installationDate"]
    lifetime_energy = site_overview["overview"]["lifeTimeData"]["energy"]
    recent_month_energy = site_overview["overview"]["lastMonthData"]["energy"]
    energy_unit = "Wh"
    return {
        "installed_on": installed_on,
        "lifetime_energy": lifetime_energy,
        "recent_month_energy": recent_month_energy,
        "energy_unit": energy_unit,
    }


def infer_quick_insights_from_energy_star_data(data, type: QuickInsightsType):
    if type == QuickInsightsType.electric_grid:
        electric_grid_data = []

        for each in data["series"]:
            if each["dataTypeId"] == 1:
                electric_grid_data = each["data"]
                break

        if not electric_grid_data:
            return {
                "installed_on": None,
                "lifetime_energy": None,
                "recent_month_energy": None,
                "energy_unit": None,
            }

        energy_unit = get_energy_unit_from_raw(data["yAxisName"])
        # first data point in the source = the first time this site is registered with energy star
        installed_on = convert_unix_time_to_datetime_string(
            electric_grid_data[0][0], only_need_date=True
        )
        lifetime_energy = sum([data_point[1] for data_point in electric_grid_data])
        # last data point in the source = the last time this site is registered with energy star
        recent_month_energy = electric_grid_data[-1][1]
    elif type == QuickInsightsType.natural_gas:
        natural_gas_data = []

        for each in data["series"]:
            if each["dataTypeId"] == 2:
                natural_gas_data = each["data"]
                break

        if not natural_gas_data:
            return {
                "installed_on": None,
                "lifetime_energy": None,
                "recent_month_energy": None,
                "energy_unit": None,
            }

        energy_unit = get_energy_unit_from_raw(data["yAxisName"])
        # first data point in the source = the first time this site is registered with energy star
        installed_on = convert_unix_time_to_datetime_string(
            natural_gas_data[0][0], only_need_date=True
        )
        lifetime_energy = sum([data_point[1] for data_point in natural_gas_data])
        # last data point in the source = the last time this site is registered with energy star
        recent_month_energy = natural_gas_data[-1][1]

    return {
        "installed_on": installed_on,
        "lifetime_energy": lifetime_energy,
        "recent_month_energy": recent_month_energy,
        "energy_unit": energy_unit,
    }


def format_solar_edge_data(sites_data: list[dict]):
    merged = defaultdict(float)
    for data in sites_data:
        energy_unit = data["sitesEnergy"]["unit"]
        for site in data["sitesEnergy"]["siteEnergyList"]:
            for entry in site["energyValues"]["values"]:
                if entry["value"]:
                    merged[entry["date"]] += entry["value"]

    merged_list = [{"date": date, "value": value} for date, value in merged.items()]
    return [
        {
            "label": QuickInsightsType.solar,
            "energy_unit": energy_unit,
            "data": merged_list,
        }
    ]


def infer_energy_star_data(data, chart_date: date, chart_type: ChartType):
    electric_grid_data = []
    natural_gas_data = []

    for each in data["series"]:
        if each["dataTypeId"] == 1:
            electric_grid_data = each["data"]
        elif each["dataTypeId"] == 2:
            natural_gas_data = each["data"]

    energy_unit = get_energy_unit_from_raw(data["yAxisName"])
    if chart_type == ChartType.Y:
        filtered_electric_grid_data = [
            {"date": convert_unix_time_to_datetime_string(unixtime), "value": value}
            for unixtime, value in electric_grid_data
            if datetime.fromtimestamp(unixtime / 1000).year == chart_date.year
        ]
        filtered_natural_gas_data = [
            {"date": convert_unix_time_to_datetime_string(unixtime), "value": value}
            for unixtime, value in natural_gas_data
            if datetime.fromtimestamp(unixtime / 1000).year == chart_date.year
        ]
    elif chart_type == ChartType.All:
        electric_grid_data_grouped_by_year = defaultdict(list)
        natural_gas_data_grouped_by_year = defaultdict(list)

        for unixtime, value in electric_grid_data:
            year = datetime.fromtimestamp(unixtime / 1000).year
            electric_grid_data_grouped_by_year[year].append(value)

        for unixtime, value in natural_gas_data:
            year = datetime.fromtimestamp(unixtime / 1000).year
            natural_gas_data_grouped_by_year[year].append(value)

        filtered_electric_grid_data = [
            {"date": convert_year_to_datetime_string(year), "value": sum(values)}
            for year, values in electric_grid_data_grouped_by_year.items()
        ]

        filtered_natural_gas_data = [
            {"date": convert_year_to_datetime_string(year), "value": sum(values)}
            for year, values in natural_gas_data_grouped_by_year.items()
        ]

    return [
        {
            "label": QuickInsightsType.electric_grid,
            "energy_unit": energy_unit,
            "data": filtered_electric_grid_data,
        },
        {
            "label": QuickInsightsType.natural_gas,
            "energy_unit": energy_unit,
            "data": filtered_natural_gas_data,
        },
    ]


def merge_sites_from_solar_edge_and_energy_star(
    solar_edge_sites_list, energy_star_sites_list, uploaded_solar_edge_sites
):
    formatted_solar_edge_sites_list = [
        {
            "id_solar_edge": site["id"],
            "name_solar_edge": site["name"],
            "custom_api_key": settings.API_KEY_SOLAR_EDGE,
        }
        for site in solar_edge_sites_list
        if site["status"] == "Active"
    ]

    for site in uploaded_solar_edge_sites:
        if site["active"]:
            formatted_solar_edge_sites_list.append(site)

    formatted_energy_star_sites_list = [
        {
            "id_energy_star": site["id"],
            "name_energy_star": site["name"],
        }
        for site in energy_star_sites_list
    ]

    solar_edge_df = pd.DataFrame(formatted_solar_edge_sites_list)
    energy_star_df = pd.DataFrame(formatted_energy_star_sites_list)

    def get_best_match(row, choices):
        name = row["name_solar_edge"]
        best_match = process.extractOne(name, choices, scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] >= NAME_SIMILARITY_THRESHOLD:
            return best_match[0]
        return None

    # Apply the function to find matches
    solar_edge_df["best_match"] = solar_edge_df.apply(
        lambda x: get_best_match(x, energy_star_df["name_energy_star"]), axis=1
    )

    # Merge the DataFrames based on the matched names
    merged_df = pd.merge(
        solar_edge_df,
        energy_star_df,
        left_on="best_match",
        right_on="name_energy_star",
        how="outer",
    )

    # Drop the temporary match column
    merged_df = merged_df.drop(columns=["best_match"])

    def determine_internal_name(row):
        if pd.notna(row["name_solar_edge"]) and pd.notna(row["name_energy_star"]):
            return f"{row['name_solar_edge']} / {row['name_energy_star']}"
        if pd.notna(row["name_solar_edge"]):
            return row["name_solar_edge"]
        if pd.notnull(row["id_energy_star"]):
            return row["name_energy_star"]
        return "No Name"

    # Add 'internal_name' column based on the conditions
    merged_df["internal_name"] = merged_df.apply(determine_internal_name, axis=1)

    # Drop rows that have NA for both of these columns
    merged_df.dropna(
        subset=["id_solar_edge", "id_energy_star"], how="all", inplace=True
    )

    # ID should be int, not float
    merged_df["id_solar_edge"] = pd.to_numeric(
        merged_df["id_solar_edge"], downcast="integer", errors="coerce"
    )
    merged_df["id_energy_star"] = pd.to_numeric(
        merged_df["id_energy_star"], downcast="integer", errors="coerce"
    )

    return merged_df
