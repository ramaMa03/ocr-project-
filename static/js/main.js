
// التحقق من رقم الهوية

function validateNationalID(id){

    if(id.length !== 10){

        alert("رقم الهوية يجب أن يتكون من 10 أرقام");

        return false;
    }

    return true;
}

// التحقق من الجوال

function validatePhone(phone){

    if(phone.length < 10){

        alert("رقم الجوال غير صحيح");

        return false;
    }

    return true;
}