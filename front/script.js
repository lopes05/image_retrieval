window.$ = window.jQuery = require('jquery'); // not sure if you need this at all
window.Bootstrap = require('bootstrap');


var dados;

function refilter() 
{   

    imgs = [];
    for (d in dados){
        var pacote = {'img': d, 'relevant': document.getElementById(d).checked};
        imgs.push(pacote);
    }
    json = JSON.stringify(imgs);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://localhost:5000/refilter', true); // or https://example.com/upload/image
    xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
    xhr.onreadystatechange = function(e) {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            console.log(xhr.responseType);
            recreate();
            loadgallery(xhr);
          } 
        }
    }
    xhr.send(json);
    
};

function recreate()
{
    var myNode = document.getElementById("realimagens");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
}


function upload_file() 
{
    let photo = document.getElementById("imgurl").files[0] // simlar to: document.getElementById("image-file").files[0] 
   

    let formData = new FormData();
    formData.append("imgurl", photo);  

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(e) {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            console.log(xhr.responseType)
            loadgallery(xhr);
          } 
        }
    }
    xhr.open("POST", 'http://localhost:5000/image', true); // or https://example.com/upload/image
    xhr.send(formData);
    
};


function loadgallery(json_data, first) {

    var arr = JSON.parse(json_data.response);
    
    str = "";
    var x = 0;
    for (ke in arr){
        
        str = str + '<div class="col-lg-3 col-md-4 col-xs-6">'
            + '<input id="' + ke + '" name="dados" type="checkbox"\> Relevante?'
            + '<a href="#" class="d-block mb-4 h-100">' + 
            '<img class="img-fluid img-thumbnail" src="/home/gustavo/GustavoUNB/tcc/corel1000/' + ke + '" alt="' + arr[ke] + '"\>'
            + "<\a> </div>";
    }
    
 
    //append the markup to the DOM
    let k = document.createRange().createContextualFragment(str);
    dados = arr;
    
    document.getElementById("formbusca").style.display="none";
    document.getElementById("imagens").style.display="block";
    document.getElementById("realimagens").append(k);
};