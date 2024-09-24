# Web App

## NVM 

* `nvm ls`
* `nvm use v20.5.0`

##  NPM
* `npm start`
* `npm test`
* `npm run build`
    * Builds the app for production to the `build` folder.\ It correctly bundles React in production mode and optimizes the build for the best performance.
* `npm run eject`

## S3 

See bucket name from Terraform: "email-snap-app-website-bucket"

* Copy content
    * `aws s3 sync ./build s3://email-snap-app-website-bucket`

* Invalidate content
    * `aws cloudfront create-invalidation --distribution-id <distribution-ID> --paths "/*"`