# FitZone - Gym Management System

FitZone is a comprehensive management system designed for gyms and fitness centers. It provides tools for managing members, trainers, and administrative staff, with secure authentication and data management capabilities.

## Features

- **User Management**: Register and manage gym members with membership details and renovation dates
- **Trainer Management**: Track trainers, their specialties, and working hours
- **Admin System**: Multi-level administrative access with secure authentication
- **Data Relationships**: Connect trainers with their manager accounts
- **Secure Authentication**: Password hashing with Argon2 for maximum security

## Technologies Used

### Backend
- **Python**: Core programming language
- **SQLAlchemy**: ORM for database interactions
- **SQLite**: Lightweight database engine
- **Argon2**: Modern password hashing algorithm

### Frontend
- **CustomTkinter**: Enhanced Tkinter UI library for a modern interface

### Development Tools
- **PrettyTable**: For formatted data visualization during development and testing
- **Unittest**: For testing application components

## Project Structure

The application follows a domain-driven design with clear separation between:
- Domain models (User, Trainer, Admin)
- Database models and ORM mappings
- Data conversion utilities
- CRUD operations
- UI components
