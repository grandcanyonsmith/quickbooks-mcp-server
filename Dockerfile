# Use Maven with OpenJDK 17 for building
FROM maven:3.9-openjdk-17 AS build

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml and source code
COPY pom.xml ./
COPY src ./src

# Download dependencies and build the application
RUN mvn clean package -DskipTests

# Use OpenJDK 17 for runtime
FROM openjdk:17-jdk-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built JAR from the build stage
COPY --from=build /app/target/quickbooks-mcp-server-1.0.0.jar app.jar

# Expose the port that the application will run on
EXPOSE 8080

# Set environment variables
ENV SPRING_PROFILES_ACTIVE=production

# Run the application
CMD ["java", "-jar", "app.jar"] 