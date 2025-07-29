package com.mcp.quickbooks.service;

import com.intuit.ipp.core.Context;
import com.intuit.ipp.core.ServiceType;
import com.intuit.ipp.data.*;
import com.intuit.ipp.exception.FMSException;
import com.intuit.ipp.security.OAuth2Authorizer;
import com.intuit.ipp.services.DataService;
import com.intuit.ipp.services.QueryResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Base64;

@Service
public class QuickBooksService {

    @Value("${quickbooks.oauth.accessToken}")
    private String accessToken;

    @Value("${quickbooks.oauth.refreshToken}")
    private String refreshToken;

    @Value("${quickbooks.oauth.realmId}")
    private String realmId;

    @Value("${quickbooks.oauth.clientId}")
    private String clientId;

    @Value("${quickbooks.oauth.clientSecret}")
    private String clientSecret;

    @Value("${quickbooks.oauth.tokenUrl}")
    private String tokenUrl;

    private LocalDateTime tokenExpiry;
    private final RestTemplate restTemplate = new RestTemplate();

    private synchronized void refreshTokenIfNeeded() {
        try {
            // Check if we need to refresh (if token expires within 5 minutes)
            if (tokenExpiry == null || LocalDateTime.now().plusMinutes(5).isAfter(tokenExpiry)) {
                System.out.println("Refreshing QuickBooks access token...");
                refreshAccessToken();
            }
        } catch (Exception e) {
            System.err.println("Failed to refresh token: " + e.getMessage());
            // Continue with existing token and let the API call fail if needed
        }
    }

    private void refreshAccessToken() {
        try {
            // Prepare the request headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
            
            // Create Basic Auth header
            String auth = clientId + ":" + clientSecret;
            String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes());
            headers.set("Authorization", "Basic " + encodedAuth);
            headers.set("Accept", "application/json");

            // Prepare the request body
            MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
            body.add("grant_type", "refresh_token");
            body.add("refresh_token", refreshToken);

            HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(body, headers);

            // Make the refresh token request
            ResponseEntity<Map> response = restTemplate.exchange(
                tokenUrl,
                HttpMethod.POST,
                request,
                Map.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();
                
                // Update the access token
                this.accessToken = (String) responseBody.get("access_token");
                
                // Update refresh token if provided (some providers rotate refresh tokens)
                if (responseBody.containsKey("refresh_token")) {
                    this.refreshToken = (String) responseBody.get("refresh_token");
                }

                // Calculate token expiry (default to 1 hour if not provided)
                Integer expiresIn = (Integer) responseBody.getOrDefault("expires_in", 3600);
                this.tokenExpiry = LocalDateTime.now().plusSeconds(expiresIn);

                System.out.println("Successfully refreshed QuickBooks access token. Expires at: " + tokenExpiry);
            } else {
                throw new RuntimeException("Failed to refresh token: " + response.getStatusCode());
            }
        } catch (Exception e) {
            System.err.println("Error refreshing access token: " + e.getMessage());
            throw new RuntimeException("Failed to refresh access token", e);
        }
    }

    private DataService getDataService() throws FMSException {
        // Automatically refresh token if needed
        refreshTokenIfNeeded();
        
        OAuth2Authorizer oauth = new OAuth2Authorizer(accessToken);
        Context context = new Context(oauth, ServiceType.QBO, realmId);
        return new DataService(context);
    }

    public Object executeQuery(String query) throws FMSException {
        try {
            DataService service = getDataService();
            QueryResult queryResult = service.executeQuery(query);
            return queryResult.getEntities();
        } catch (FMSException e) {
            // Check if this is an authentication error
            if (e.getMessage() != null && e.getMessage().contains("401")) {
                System.out.println("Authentication failed, forcing token refresh...");
                this.tokenExpiry = LocalDateTime.now().minusMinutes(1); // Force refresh
                refreshTokenIfNeeded();
                
                // Retry the query with the new token
                DataService service = getDataService();
                QueryResult queryResult = service.executeQuery(query);
                return queryResult.getEntities();
            }
            throw e;
        }
    }

    public Object createEntity(String entityType, Map<String, Object> entityData) throws FMSException {
        try {
            DataService service = getDataService();
            
            switch (entityType.toLowerCase()) {
                case "customer":
                    return createCustomer(service, entityData);
                case "item":
                    return createItem(service, entityData);
                case "invoice":
                    return createInvoice(service, entityData);
                default:
                    throw new IllegalArgumentException("Unsupported entity type: " + entityType);
            }
        } catch (FMSException e) {
            // Check if this is an authentication error
            if (e.getMessage() != null && e.getMessage().contains("401")) {
                System.out.println("Authentication failed, forcing token refresh...");
                this.tokenExpiry = LocalDateTime.now().minusMinutes(1); // Force refresh
                refreshTokenIfNeeded();
                
                // Retry the operation with the new token
                return createEntity(entityType, entityData);
            }
            throw e;
        }
    }

    private Customer createCustomer(DataService service, Map<String, Object> data) throws FMSException {
        Customer customer = new Customer();
        customer.setDisplayName((String) data.get("name"));
        
        if (data.get("email") != null) {
            EmailAddress email = new EmailAddress();
            email.setAddress((String) data.get("email"));
            customer.setPrimaryEmailAddr(email);
        }
        
        if (data.get("phone") != null) {
            TelephoneNumber phone = new TelephoneNumber();
            phone.setFreeFormNumber((String) data.get("phone"));
            customer.setPrimaryPhone(phone);
        }

        return service.add(customer);
    }

    private Item createItem(DataService service, Map<String, Object> data) throws FMSException {
        Item item = new Item();
        item.setName((String) data.get("name"));
        item.setType(ItemTypeEnum.INVENTORY);
        
        if (data.get("unitPrice") != null) {
            item.setUnitPrice(java.math.BigDecimal.valueOf(((Number) data.get("unitPrice")).doubleValue()));
        }

        return service.add(item);
    }

    private Invoice createInvoice(DataService service, Map<String, Object> data) throws FMSException {
        Invoice invoice = new Invoice();
        
        // Set customer reference
        if (data.get("customerId") != null) {
            ReferenceType customerRef = new ReferenceType();
            customerRef.setValue(data.get("customerId").toString());
            invoice.setCustomerRef(customerRef);
        }

        return service.add(invoice);
    }

    // Getter method for accessing current access token (useful for debugging)
    public String getCurrentAccessToken() {
        return accessToken;
    }

    // Method to check token expiry status
    public boolean isTokenExpired() {
        return tokenExpiry != null && LocalDateTime.now().isAfter(tokenExpiry);
    }

    // Method to get token expiry time
    public LocalDateTime getTokenExpiry() {
        return tokenExpiry;
    }
}