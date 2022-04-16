# School Management System API

## Features
- Register a new student.
- Add study materials.
- Add classes.
- Add academic years.
- Recording the absence of students.
- Recording students' grades
- Students promotion.
- User Login.
- User permissions.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

It's best to install Python projects in a Virtual Environment. Once you have set up a VE, clone this project

```
git clone https://github.com/Ho011/small_sms_api.git
```

```
cd small_school_management_system_api
```

```
pip install -r requirements.txt
```

### Environment Variables

The application uses an .env file to manage environment varialbes. A `.env.example` file is included in the project for your modification. (Remember to rename the file to `.env` in order for your environment variables to be read.)

The configuration can be changed to use the OS environment based on the FastAPI Settings documentation if you prefer.


```
alembic upgrade head
```

## Note

**you must create a postgres database the same as your env, before running alembic upgrade head.**


### Get Up and running

Once the prerequisites are met, The following steps can be used to get the application up and running. All commands are run from the root directory of the project

```
uvicorn app.main:app --reload
```

## Note
This project is in progress, there may be several bugs.
So if you discover that there are any errors, please fix them, and if you want to improve or add something, your **contribution is welcome.**