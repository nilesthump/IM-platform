FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /im-go .

FROM alpine:3.21
COPY --from=build /im-go /im-go
ENTRYPOINT ["/im-go"]
