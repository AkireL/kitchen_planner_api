<a name="readme-top"></a>

<div align="center">

## Recipe API - Kitchen Planner

</div>

Kitchen Planner is a powerful and efficient API designed to simplify meal planning. It allows users to manage recipes, create weekly menus, and store ingredients with ease.

## Technologies Used

- **FastAPI** - Framework for API development.
- **MySQL** - Relational database.
- **Tortoise ORM** - ORM used for data management.
- **JWT (JSON Web Token)** - Secure authentication for users.
- **Docker** - Application containerization.
- **Uvicorn** - ASGI server for the local environment.
- **Mangum** - Adapter for AWS Lambda deployment.

## Installation and Setup

### Using Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/your_user/your_repository.git
   cd your_repository
   ```
2. Configure environment variables in a `.env` file.
3. Build and run the Docker container:
   ```bash
   docker compose up --build
   ```

### Deployment on AWS

For execution on AWS Lambda, **Mangum** is used as an adapter. Different files are used depending on the environment:

- **AWS Deployment:** `lambda_handler.py`

Package and deploy the application to AWS Lambda.

## API Usage

Once authenticated, include the JWT token in the headers of protected requests:

```http
Authorization: Bearer your_token_here
```

## Dependencies

All dependencies required to run the application are listed in the `requirements.txt` file.

## Contributions

If you would like to contribute, open an issue or submit a pull request with your improvements.

## License

This project is licensed under the MIT License.
