    
# rmSMS

rmSMS is a simple notification app designed for the purpose of receiving SMS from a mobile phone.

It accomplishes this, by connecting to a remote server (of your choice), which is capable of serving its data in JSON format to be consumed by rmSMS (a server API is included in the repo).

It is Linux and Windows compatible, can use audio/visual notifications and has some further customization options as well.

A separate simple API, with rudimentary encryption capabilities (if supplied with a key otherwise unencrypted), can be found within the 'server' directory in the repo.

Do note that a separate mobile application, able to send the SMS (in JSON format) to the API server is also required and not supplied here.

Regardless, if you have the know-how, rmSMS is able to consume JSON data and notify, so the implementation is yours to decide.

This was made for personal use, and it does not follow any serious security rules, just Simple HTTP Auth, HTTPs and a rudimentary encryption for the data in rest (if enabled) for the server. Thus it is secure enough, in my opinion, for personal use.

## License

This project is made available under the AGPL 3.0 or later License.

