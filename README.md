    
# rmSMS

rmSMS is a simple notification app designed for the purpose of receiving SMS from a mobile phone.

It accomplishes this, by connecting to a remote asset, which serves its data in JSON format to be consumed by rmSMS.

It is Linux and Windows compatible (it has MACOS foundations but nothing concrete), will use audio and visual notifications to alert the user and has some customization options as well.

A separate simple API will also be published at some point in the future, which is needed for this app to connect and consume data.

Do note that a separate mobile application able to send the SMS (in JSON format) to the API server is also needed and not supplied here.

Regardless, if you have the know how, rmSMS is able to consume JSON data and notify, so the implementation is yours to decide.

This was made for personal use, and it does not follow any serious security rules, just Simple Auth and HTTPs for the server, since it relies on personal user obscurity (your server, no response to unauthorized requests, etc.) and it is secure enough, in my opinion, for personal use.

## License

This project is made available under the AGPL 3.0 or later License.

