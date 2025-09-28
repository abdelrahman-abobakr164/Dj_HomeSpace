let pmessage = document.getElementById("id_p");
let authmessage = document.getElementById("id_ptag");

let loginform = document.getElementById("customloginform");
let signupform = document.getElementById("signupForm");
let sendemailform = document.getElementById("sendemailForm");
let resetform = document.getElementById("resetForm");
let changeform = document.getElementById("changeform");
let my_accountform = document.getElementById("myaccountForm");
let contactform = document.getElementById("contactForm");
let serviceform = document.getElementById("serviceForm");
let phoneform = document.getElementById("phoneForm");
let propertyform = document.getElementById("propertyForm");
let contactagentform = document.getElementById("contactagentForm");

let subjectfield = document.querySelector("[name='subject']");
let schedule_datefield = document.querySelector("[name='schedule_date']");
let property_property_type = document.querySelector("[name='property_type']");
let property_name = document.querySelector("[name='name']");
let property_main_image = document.querySelector("[name='main_image']");
let property_address = document.querySelector("[name='address']");
let property_rent = document.querySelector("[name='rent']");
let property_price = document.querySelector("[name='price']");
let property_security_deposit = document.querySelector("[name='security_deposit']");
let property_bathrooms = document.querySelector("[name='bathrooms']");
let property_bedrooms = document.querySelector("[name='bedrooms']");
let property_meter = document.querySelector("[name='meter']");
let property_description = document.querySelector("[name='description']");
let property_category = document.querySelector("[name='category']");
let property_available_at = document.querySelector("[name='available_at']");

let loginfield = document.querySelector("[name='login']");
let passwordfield = document.querySelector("[name='password']");
let usernamefield = document.querySelector("[name='username']");
let emailfield = document.querySelector("[name='email']");
let phonefield = document.querySelector("[name='phone']");
let imagefield = document.querySelector("[name='image']");
let password1field = document.querySelector("[name='password1']");
let password2field = document.querySelector("[name='password2']");
let oldpasswordfield = document.querySelector("[name='oldpassword']");
let messagefield = document.querySelector("[name='mesasge']");


if (loginform) {
    loginform.onsubmit = function (e) {
        if (loginfield.value === '' || passwordfield.value === '') {
            authmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
}

if (signupform) {
    signupform.onsubmit = function (e) {
        if (usernamefield.value === '' || emailfield.value === '' || password1field.value === '' || password2field.value === '' || phonefield.value === '' || imagefield.value === '') {
            authmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
} 

if (sendemailform) {
    sendemailform.onsubmit = function (e) {
        if (emailfield.value === '' ) {
            authmessage.innerHTML = 'This Field is Required';
            e.preventDefault();
        } 
    };
} 

if (resetform) {
    resetform.onsubmit = function (e) {
        if (password1field.value === '' || password2field.value === '' ) {
            authmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
} 

if (changeform) {
    changeform.onsubmit = function (e) {
        if (password1field.value === '' || password2field.value === '' || oldpasswordfield.value === '') {
            authmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
} 

if (contactagentform) {
    contactagentform.onsubmit = function (e) {
        if (subjectfield.value === '' || schedule_datefield.value === '' || phonefield.value === '') {
            pmessage.innerHTML = 'The Fields has Asterisk Sign Are Required';
            e.preventDefault();
        } 
    };
} 

if (contactform) {
    contactform.onsubmit = function (e) {
        if (emailfield.value === '' || messagefield.value === '') {
            pmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
} 

if (serviceform) {
    serviceform.onsubmit = function (e) {
        if (emailfield.value === '' || messagefield.value === '' || username.value === '') {
            pmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
        } 
    };
} 

if (my_accountform) {
    my_accountform.onsubmit = function (e) {
        if (usernamefield.value === '' || phonefield.value === '' ) {
            authmessage.innerHTML = 'All Fields are Required';
            e.preventDefault();
            
        }
    };
} 

if (propertyform) {
    if (property_property_type.value === 'for-sale') {
        property_price.required = true;
    }if (property_property_type.value === 'for-rent') {
        property_rent.required = true;
        property_security_deposit.required = true;
    }
    propertyform.onsubmit = function (e) {
        if (property_property_type.value == 'for-sale') {
            if (property_price.value === '' ||
                property_name.value === '' ||
                property_main_image.value === '' ||
                property_address.value === '' ||
                property_bathrooms.value === '' ||
                property_bedrooms.value === '' ||
                property_meter.value === '' ||
                property_description.value === '' ||
                property_category.value === '' ||
                property_available_at.value === '') {
                    pmessage.innerHTML = 'All Fields are Required';
                    e.preventDefault();
            }

        }if (property_property_type.value == 'for-rent') {
            if (property_name.value === '' ||
                property_main_image.value === '' ||
                property_address.value === '' ||
                property_rent.value === '' ||
                property_security_deposit.value === '' ||
                property_bathrooms.value === '' ||
                property_bedrooms.value === '' ||
                property_meter.value === '' ||
                property_description.value === '' ||
                property_category.value === '' ||
                property_available_at.value === '') {
                    pmessage.innerHTML = 'All Fields are Required';
                    e.preventDefault();
            }

        }
    };
} 

if (phoneform) {
    phoneform.onsubmit = function (e) {
        if (phonefield.value === '' ) {
            pmessage.innerHTML = 'This Field is Required';
            e.preventDefault();  
        }
    };
} 