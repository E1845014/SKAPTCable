# SKAPTCable

SKAPTCable is a Django-based web application designed to manage cable company operations. This project includes modules for handling various aspects of the business, such as customer management, employee management, and payment processing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

To get started with SKAPTCable, follow these steps:

1. Clone the repository:

   ```sh
   git clone https://github.com/E1845014/SKAPTCable.git
   cd skaptcable
   cd skapt_cable_company
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Apply the migrations:

   ```sh
   python manage.py migrate
   ```

5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Usage

Once the development server is running, you can access the application at `http://127.0.0.1:8000/`. From there, you can navigate through the different sections of the application to manage customers, employees, areas, and payments.

## Features

- **Customer Management**: Add, update, and delete customer information.
- **Employee Management**: Manage employee records and roles.
- **Payment Processing**: Handle customer payments and generate invoices.
- **Area Management**: Handle areas under service
- **Admin Interface**: Use Django's built-in admin interface for advanced management.

## Contributing

We welcome contributions to SKAPTCable! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and commit them with clear and concise messages.
4. Push your changes to your fork.
5. Open a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](http://_vscodecontentref_/1) file for more details.
