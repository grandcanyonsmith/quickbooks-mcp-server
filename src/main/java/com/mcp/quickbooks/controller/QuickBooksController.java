package com.mcp.quickbooks.controller;

import com.mcp.quickbooks.service.QuickBooksService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/quickbooks")
@CrossOrigin(origins = "*")
public class QuickBooksController {

    @Autowired
    private QuickBooksService quickBooksService;

    @PostMapping("/query")
    public ResponseEntity<?> executeQuery(@RequestBody Map<String, String> request) {
        try {
            String query = request.get("query");
            Object result = quickBooksService.executeQuery(query);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Failed to execute query: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @PostMapping("/create")
    public ResponseEntity<?> createEntity(@RequestBody Map<String, Object> request) {
        try {
            String entityType = (String) request.get("entityType");
            Map<String, Object> entityData = (Map<String, Object>) request.get("entityData");
            
            Object result = quickBooksService.createEntity(entityType, entityData);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Failed to create entity: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/token/status")
    public ResponseEntity<Map<String, Object>> getTokenStatus() {
        Map<String, Object> status = new HashMap<>();
        try {
            LocalDateTime expiry = quickBooksService.getTokenExpiry();
            boolean isExpired = quickBooksService.isTokenExpired();
            
            status.put("isExpired", isExpired);
            status.put("expiryTime", expiry != null ? expiry.toString() : "Unknown");
            status.put("currentTime", LocalDateTime.now().toString());
            
            if (expiry != null) {
                long minutesUntilExpiry = java.time.Duration.between(LocalDateTime.now(), expiry).toMinutes();
                status.put("minutesUntilExpiry", minutesUntilExpiry);
            }
            
            status.put("status", "Active");
            return ResponseEntity.ok(status);
        } catch (Exception e) {
            status.put("error", "Failed to get token status: " + e.getMessage());
            return ResponseEntity.badRequest().body(status);
        }
    }

    @PostMapping("/token/refresh")
    public ResponseEntity<Map<String, Object>> forceTokenRefresh() {
        Map<String, Object> response = new HashMap<>();
        try {
            // This will trigger a refresh by making a simple query
            String testQuery = "SELECT COUNT(*) FROM CompanyInfo";
            quickBooksService.executeQuery(testQuery);
            
            response.put("message", "Token refresh completed successfully");
            response.put("newExpiryTime", quickBooksService.getTokenExpiry() != null ? 
                quickBooksService.getTokenExpiry().toString() : "Unknown");
            response.put("currentTime", LocalDateTime.now().toString());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("error", "Failed to refresh token: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
}