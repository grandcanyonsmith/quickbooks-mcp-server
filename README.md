# QuickBooks MCP Server

A Spring Boot application that provides a web dashboard for QuickBooks expense management with vendor normalization and automatic token refresh.

## Features

- 📊 **Real-time QuickBooks Integration** - Live expense data from QuickBooks API
- 🔄 **Automatic Token Refresh** - No manual token updates needed
- 🏷️ **Vendor Name Normalization** - Clean up messy transaction descriptions
- 🏢 **Department Categorization** - Organize expenses by business units
- 📅 **Date Range Filtering** - Filter expenses by custom date ranges
- 📈 **Interactive Dashboard** - Charts, grouping, and detailed transaction views
- ⚙️ **Transformation Rules** - Manage vendor normalization rules

## Local Development

### Prerequisites
- Java 17 or higher
- Maven 3.6+
- QuickBooks Developer Account

### Setup
1. Clone the repository
2. Configure your QuickBooks OAuth credentials in `application.properties`
3. Run the application:
   ```bash
   mvn spring-boot:run
   ```
4. Open http://localhost:8080

## Deployment

### Environment Variables
Configure these environment variables in your deployment platform:

- `QUICKBOOKS_ACCESS_TOKEN` - Your QuickBooks access token
- `QUICKBOOKS_REFRESH_TOKEN` - Your QuickBooks refresh token  
- `QUICKBOOKS_REALM_ID` - Your QuickBooks company ID
- `QUICKBOOKS_CLIENT_ID` - Your QuickBooks app client ID
- `QUICKBOOKS_CLIENT_SECRET` - Your QuickBooks app client secret
- `PORT` - Server port (default: 8080)
- `SPRING_PROFILES_ACTIVE` - Set to "production" for deployment

### Deploy to Railway
1. Fork/clone this repository
2. Sign up at [railway.app](https://railway.app)
3. Connect your GitHub repository
4. Set the environment variables in Railway dashboard
5. Deploy!

## API Endpoints

- `GET /` - Main dashboard
- `GET /rules.html` - Transformation rules management
- `POST /api/v1/quickbooks/query` - Execute QuickBooks queries
- `GET /api/v1/quickbooks/token/status` - Check token status
- `POST /api/v1/quickbooks/token/refresh` - Force token refresh

## Security

- All sensitive configuration uses environment variables
- HTTPS required for production QuickBooks API access
- Automatic token refresh prevents expired credentials

## License

MIT License 