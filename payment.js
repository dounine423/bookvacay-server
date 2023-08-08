import axios from "axios";
import crypto from 'crypto'

const onExportCSVAllData = async () => {
    // let fileName = moment().format('YYYY-MM-DD+HH:mm:ss') + ".csv"
    // API.post('/getHotelBookCSVByAdmin', {
    //   data: 'some data'
    // }, {
    //   responseType: 'blob'
    // }).then(response => {
    //   const url = window.URL.createObjectURL(new Blob([response.data]));
    //   const link = document.createElement('a');
    //   link.href = url;
    //   link.setAttribute('download', fileName);
    //   document.body.appendChild(link);
    //   link.click();
    // });

    const myData = {
        merchant_id: "13307418",
        merchant_key: "2k6snwb8basud",
        email_address: "dounine423@gmail.com",
        m_payment_id: "00001",
        amount: 50,
        item_name: "#00001",
    };
    myData["signature"] = generateSignature(myData);
    const pfParamString = dataToString(myData);
    const identifier = await generatePaymentIdentifier(pfParamString);
    console.log("identifier", identifier)

    payfast_do_onsite_payment({ "uuid": identifier }, function (result) {
        if (result === true) {
            console.log("Success Payment")
        }
        else {
            console.log("Failded Payment")
        }
    });
}

const generatePaymentIdentifier = async (pfParamString) => {
    const result = await axios.post('https://www.payfast.co.za/onsite/process', pfParamString)
        .then((res) => {
            return res.data.uuid || null;
        })
        .catch((error) => {
            console.error(error)
        });
    return result;
};

const generateSignature = (data, passPhrase = null) => {
    let pfOutput = "";
    for (let key in data) {
        if (data.hasOwnProperty(key)) {
            if (data[key] !== "") {
                pfOutput += `${key}=${encodeURIComponent(data[key]).replace(/%20/g, "+")}&`
            }
        }
    }
    let getString = pfOutput.slice(0, -1);
    if (passPhrase !== null) {
        getString += `&passphrase=${encodeURIComponent(passPhrase).replace(/%20/g, "+")}`;
    }
    return crypto.createHash("md5").update(getString).digest("hex");
};

const dataToString = (dataArray) => {
    let pfParamString = "";
    for (let key in dataArray) {
        if (dataArray.hasOwnProperty(key)) { pfParamString += `${key}=${encodeURIComponent(dataArray[key]).replace(/%20/g, "+")}&`; }
    }
    return pfParamString.slice(0, -1);
};

useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://www.payfast.co.za/onsite/engine.js";
    script.async = true;
    document.body.appendChild(script);
    if (request) {
        getData()
    }
}, [request])