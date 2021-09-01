serviceName: ${SERVICE_NAME}
containers:
  nginx:
    command: []
    image: ${LATEST_NGINX_IMAGE}
    ports:
      "80": HTTP
  app:
    command: []
    environment:
      ACTVATION_FRONTEND_URL: "${ACTVATION_FRONTEND_URL}"
      ACTIVATION_URL: "${ACTIVATION_URL}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_S3_REGION_NAME: "${AWS_S3_REGION_NAME}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_STORAGE_BUCKET_NAME: "${AWS_STORAGE_BUCKET_NAME}"
      DATABASE_HOST: "${DATABASE_HOST}"
      DATABASE_NAME: "${DATABASE_NAME}"
      DATABASE_PASSWORD: "${DATABASE_PASSWORD}"
      DATABASE_USER: "${DATABASE_USER}"
      DATA_UPLOAD_MAX_NUMBER_FIELDS: "${DATA_UPLOAD_MAX_NUMBER_FIELDS}"
      EMAIL_BACKEND: "${EMAIL_BACKEND}"
      EVENT_SIGNUPS_OPEN: "${EVENT_SIGNUPS_OPEN}"
      EVENT_SIGNUPS_CLOSE: "${EVENT_SIGNUPS_CLOSE}"
      GASTRO_SIGNUPS_OPEN: "${GASTRO_SIGNUPS_OPEN}"
      GASTRO_SIGNUPS_CLOSE: "${GASTRO_SIGNUPS_CLOSE}"
      MAILJET_API_KEY: "${MAILJET_API_KEY}"
      MAILJET_SECRET_KEY: "${MAILJET_SECRET_KEY}"
      MAPBOX_ACCESS_TOKEN: "${MAPBOX_ACCESS_TOKEN}"
      MAPBOX_USERNAME: "${MAPBOX_USERNAME}"
      PASSWORD_RESET_CONFIRM_FRONTEND_URL: "${PASSWORD_RESET_CONFIRM_FRONTEND_URL}"
      PASSWORD_RESET_CONFIRM_URL: "${PASSWORD_RESET_CONFIRM_URL}"
      PLAYSTREET_RECIPIENT: "${PLAYSTREET_RECIPIENT}"
      NEWSLETTER_LIST_ID: "${NEWSLETTER_LIST_ID}"
      REPORTS_NOTIFICATION_CAMPAIGN: "${REPORTS_NOTIFICATION_CAMPAIGN}"
      REPORTS_NOTIFICATION_SENDER: "${REPORTS_NOTIFICATION_SENDER}"
      TOGGLE_GASTRO_DIRECT_SIGNUP: "${TOGGLE_GASTRO_DIRECT_SIGNUP}"
      TOGGLE_GASTRO_REGISTRATIONS: "${TOGGLE_GASTRO_REGISTRATIONS}"
      TOGGLE_NEWSLETTER: "${TOGGLE_NEWSLETTER}"
      USE_X_FORWARDED_FOR: "${USE_X_FORWARDED_FOR}"
    image: ${LATEST_APP_IMAGE}
publicEndpoint:
  containerName: nginx
  containerPort: 80
  healthCheck:
    healthyThreshold: 2
    intervalSeconds: 20
    path: /
    successCodes: 200-499
    timeoutSeconds: 4
    unhealthyThreshold: 2
