# Chemical Equipment Parameter Visualizer

A hybrid application that transforms raw CSV sensor data into actionable insights, solving common industrial challenges through consistent data visualization across both web and desktop platforms.

## Project Overview

This application provides:
- CSV sensor data import and processing
- Real-time data visualization through interactive charts
- Consistent user experience across web and desktop platforms
- PDF report generation and download functionality
- Centralized backend with shared business logic

## Architecture

The project follows a hybrid architecture with three main components:

```
chemical-equipment-visualizer/
├── backend/              # Django REST API
├── frontend-web/         # React web application
└── frontend-desktop/     # PyQt5 desktop application
```

## Live Deployment

- Backend API: https://chemical-equipment-visualizer-production-999d.up.railway.app
- Web Application: https://equipment-visualizer-735d.up.railway.app

## Technology Stack

### Backend
- Django 
- Django REST Framework
- SQLite Database
- Python 3.13.7

### Frontend Web
- React
- Create React App
- Axios for API communication

### Frontend Desktop
- PyQt5
- Python 3.13.7
- PyInstaller for executable generation

## Prerequisites

### For Backend Development
- Python 3.13.7 or higher
- pip package manager

### For Frontend Web Development
- Node.js (v14 or higher)
- npm or yarn

### For Frontend Desktop Development
- Python 3.13.7 or higher
- Windows OS (tested on Windows)

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000

### Frontend Web Setup

1. Navigate to the frontend-web directory:
```bash
cd frontend-web
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The web application will be available at http://localhost:3000

### Frontend Desktop Setup

1. Navigate to the frontend-desktop directory:
```bash
cd frontend-desktop
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

## Building Desktop Executable

To create a standalone Windows executable:

1. Navigate to the frontend-desktop directory:
```bash
cd frontend-desktop
```

2. Ensure PyInstaller is installed:
```bash
pip install pyinstaller
```

3. Build the executable:
```bash
pyinstaller --clean EquipmentVisualizer.spec
```

4. The executable will be created at:
```bash
.\frontend-desktop\dist\EquipmentVisualizer.exe
```

5. Run the executable:
```bash
.\dist\EquipmentVisualizer.exe
```

## Features

### Data Import
- Import equipment sensor data from CSV files
- Sample data file included: `sample_equipment_data.csv`

### Data Visualization
- Interactive charts and graphs
- Real-time data processing
- Consistent visualization across web and desktop platforms

### Report Generation
- Download equipment reports as PDF
- Click-to-download functionality
- Automated report formatting

### Cross-Platform Support
- Web application accessible from any modern browser
- Desktop application for Windows with offline capabilities

## Project Structure

### Backend
```
backend/
├── config/              # Django configuration
├── equipment/           # Equipment app
├── venv/               # Virtual environment
├── db.sqlite3          # SQLite database
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

### Frontend Web
```
frontend-web/
├── src/
│   ├── App.js          # Main application component
│   ├── App.css         # Application styles
│   └── ...
├── public/
└── package.json
```

### Frontend Desktop
```
frontend-desktop/
├── ui/                        # UI components
├── build/                     # Build artifacts
├── dist/                      # Distribution folder
│   └── EquipmentVisualizer.exe  # Built executable
├── main.py                    # Application entry point
├── EquipmentVisualizer.spec   # PyInstaller specification
├── requirements.txt           # Python dependencies
├── equipment_report_12.pdf    # Sample reports
├── equipment_report_13.pdf
├── equipment_report_14.pdf
├── equipment_report_15.pdf
├── equipment_report_17.pdf
├── equipment_report_22.pdf
└── sample_equipment_data.csv  # Sample data file
```

## Configuration

### Backend Configuration
The backend is configured to accept requests from both local development and production deployments. Update the `ALLOWED_HOSTS` in `backend/config/settings.py` if deploying to a new domain.

### Frontend Configuration
Update API endpoint URLs in the frontend applications to point to your backend:

For Web: Update API base URL in the React application
For Desktop: Update API base URL in the PyQt5 application

## Usage

### Using the Web Application

1. Navigate to https://equipment-visualizer-735d.up.railway.app
2. Upload your CSV file containing equipment sensor data
3. View the generated visualizations
4. Click the download button to generate and download PDF reports

### Using the Desktop Application

1. Run `EquipmentVisualizer.exe` from the dist folder
2. Upload your CSV file containing equipment sensor data
3. View the generated visualizations
4. Click the download button to generate and download PDF reports

### Sample Data

A sample CSV file (`sample_equipment_data.csv`) is included in the `frontend-desktop` directory for testing purposes.

## Development Workflow

### Making Changes to Backend
1. Make your changes in the `backend` directory
2. Test locally using `python manage.py runserver`
3. Deploy to Railway for production updates

### Making Changes to Frontend Web
1. Make your changes in the `frontend-web` directory
2. Test locally using `npm start`
3. Build using `npm run build`
4. Deploy to Railway for production updates

### Making Changes to Frontend Desktop
1. Make your changes in the `frontend-desktop` directory
2. Test using `python main.py`
3. Rebuild executable using `pyinstaller --clean EquipmentVisualizer.spec`

## Database

The application uses SQLite for data storage. The database file (`db.sqlite3`) is located in the `backend` directory.

For production deployments, consider migrating to PostgreSQL or MySQL for better performance and scalability.

## Troubleshooting

### Backend Issues
- Ensure Python 3.13.7 is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that migrations are up to date: `python manage.py migrate`

### Frontend Web Issues
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that the API URL is correctly configured

### Frontend Desktop Issues
- Ensure Python 3.13.7 is installed
- Verify PyQt5 is properly installed: `pip install PyQt5`
- Check that the API URL points to the correct backend
- If executable doesn't run, try rebuilding with PyInstaller

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly across all platforms
5. Submit a pull request

## License

This project is for educational and industrial use.

## Contact

For issues, questions, or contributions, please open an issue in the GitHub repository.
