#!/bin/bash
set -o errexit

echo "Installing dependencies and building application..."
mvn clean package -DskipTests -Dmaven.javadoc.skip=true

echo "Build completed successfully!"
ls -la target/ 