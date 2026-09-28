FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY InfraPlaceholder.java .
RUN javac InfraPlaceholder.java

FROM eclipse-temurin:25-jre-alpine
WORKDIR /app
COPY --from=build /src/InfraPlaceholder.class .
ENTRYPOINT ["java", "InfraPlaceholder"]
