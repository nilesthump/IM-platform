FROM maven:3.9.15-eclipse-temurin-25 AS build
WORKDIR /src
COPY pom.xml Main.java ./
COPY core/auth/*.java core/auth/
COPY core/im/*.java core/im/
COPY gateway/auth/*.java gateway/auth/
COPY plugin-host/*.java plugin-host/
COPY shared/authsupport/*.java shared/authsupport/
COPY tests/auth/*.java tests/auth/
RUN mvn -B -Dim.build.dir=/build package

FROM eclipse-temurin:25-jre-alpine
WORKDIR /app
COPY --from=build /build/java-profile-1.0.0.jar app.jar
ENV IM_CONFIG_FILE=/run/im-config/config.json
ENTRYPOINT ["java", "-jar", "app.jar"]
