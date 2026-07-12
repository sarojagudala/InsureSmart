// Display welcome message
window.onload = function(){

    console.log("InsureSmart Loaded Successfully");

}

// BMI Validation
function validateBMI(){

    let bmi=document.getElementsByName("bmi")[0].value;

    if(bmi<10 || bmi>60){

        alert("Please enter a valid BMI");

        return false;

    }

    return true;

}

// Age Validation
function validateAge(){

    let age=document.getElementsByName("age")[0].value;

    if(age<18){

        alert("Minimum age should be 18");

        return false;

    }

    return true;

}

// Income Validation
function validateIncome(){

    let income=document.getElementsByName("income")[0].value;

    if(income<10000){

        alert("Please enter a valid income");

        return false;

    }

    return true;

}
