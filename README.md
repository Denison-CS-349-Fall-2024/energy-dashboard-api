<!-- # energy-dashboard-api

## Spin up local dev env
1. create .env file and ask Loc/Duc to share the content of this file
2. "python3 -m venv venv" to create virtual env
3. "source venv/bin/activate" to activate virtual env
4. "pip install -r requirements.txt" to install dependencies
5. "uvicorn app.main:app --reload" to run FastAPI app
6. http://localhost:8000 -->

# **Energy Dashboard API**

The backend service for managing data and APIs for the Energy Dashboard.

---

## **Table of Contents**
1. [Overview](#overview)  
2. [Technologies Used](#technologies-used)  
3. [Setup for Local Development](#setup-for-local-development)  
4. [Usage](#usage)  
5. [License](#license)

---

## **Overview**

The **Energy Dashboard API** serves as the core backend service, providing RESTful APIs to handle energy usage data, manage database interactions, and process business logic. This API supports the Energy Dashboard UI by delivering clean and reliable data.

---

## **Technologies Used**
- **Backend Framework**: FastAPI  
- **Language**: Python 
- **Database**: Firebase  
- **Environment Management**: Python Virtual Environment  
- **Server**: Uvicorn  

---

## **Setup for Local Development**

Follow these steps to spin up a local development environment:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Denison-CS-349-Fall-2024/energy-dashboard-api.git
    cd energy-dashboard-api
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment**:
    ```bash
    source venv/bin/activate
    ```

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the FastAPI application**:
    ```bash
    uvicorn app.main:app --reload
    ```

6. **Access the API in your browser**:
    ```
    http://localhost:8000/
    ```

---

## **Usage**

- Use the **base URL** `http://localhost:8000` to interact with the API.
- Test available endpoints with tools like **Postman** or `curl`.
 

---

## **License**

This project is licensed under the [MIT License](LICENSE).
