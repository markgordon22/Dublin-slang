function sendMail() {
var params = {
        from_name: "Irish Slang",
        first_name: document.getElementById("fname").value,
        last_name: document.getElementById("lname").value,
        from: "markgordon97@gmail.com",
        to: document.getElementById("email-address").value,
        message: document.getElementById("msg").value
    };
  
  emailjs.send("service_4b99rtc","template_nllrsno",params)
   .then(
        // Alert sent if email successful
    function(response){
            alert("Your email has been sent, we will be in touch as soon as possible");
            location.reload();
},
        // Alert not sent if email was unsuccessful
    function(error) {
            alert("Your email was not sent, please try again");
            location.reload();
        }
   );
   
return false; //prevents page reloading immediately
}