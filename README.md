# Real Estate Management System

A comprehensive Flask-based real estate management system with user authentication, property listings, and admin capabilities.

## Features

- **User Authentication**: Secure registration and login system
- **Property Management**: Add, edit, and delete property listings
- **Image Upload**: Support for property images
- **Search & Filter**: Advanced property search functionality
- **Admin Panel**: Comprehensive admin dashboard for managing properties and users
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd real-estate-management
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///real_estate.db
UPLOAD_FOLDER=static/uploads
```

5. **Initialize the database**
```bash
python setup_database.py
```

6. **Run the application**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Default Admin Credentials

- **Username**: admin
- **Password**: admin123

**Important**: Change the admin password after first login!

## Project Structure

```
real-estate-management/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── admin.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── properties/
│   │   └── admin/
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/
├── migrations/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
├── setup_database.py
└── run.py
```

## Usage

### For Users
1. Register a new account or login
2. Browse available properties
3. Use search and filters to find properties
4. View detailed property information

### For Admins
1. Login with admin credentials
2. Access the admin panel
3. Add, edit, or delete properties
4. Manage user accounts
5. View system statistics

## Features in Detail

### Property Listings
- Property title and description
- Price and location information
- Property type (apartment, house, commercial, etc.)
- Number of bedrooms and bathrooms
- Area in square feet
- Multiple image support
- Available/Sold status

### Search & Filter
- Search by location, price range, property type
- Filter by number of bedrooms/bathrooms
- Sort by price, date added, etc.

### Admin Dashboard
- User management
- Property management
- Statistics and analytics
- Bulk operations

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- Secure file upload handling
- SQL injection protection with SQLAlchemy

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Email notifications
- [ ] Advanced search with map integration
- [ ] Property comparison feature
- [ ] Saved searches and favorites
- [ ] Mobile application
- [ ] Payment integration
- [ ] Multi-language support

## Acknowledgments

- Flask documentation
- Bootstrap framework
- SQLAlchemy ORM
- Flask community