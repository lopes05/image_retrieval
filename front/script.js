window.$ = window.jQuery = require('jquery'); // not sure if you need this at all


var dados;

function refilter() 
{   

    imgs = [];
    var sel = document.getElementById('selectbox');
    var tec = document.getElementById('tecnica');
    for (d in dados){
        el = document.getElementById(d + "d");
        el2 = document.getElementById(d + "i");

        if(d.includes(sel.value)){
            el.checked = true;
            el2.checked = false;
        }
        else{
            el.checked = false;
            el2.checked = true;
        }

        var pacote = {'img': d, 'relevant': el.checked, 'irrelevant': el2.checked };
        imgs.push(pacote);
    }
    imgs.push({'classname': sel.value});
    imgs.push({'tecnica': tec.value});
    json = JSON.stringify(imgs);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://localhost:5000/refilter', true);
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
};


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
            var element = document.getElementById("footer");
            element.classList.remove("position-fixed");
            element.classList.add("position-relative");
          } 
        }
    }
    xhr.open("POST", 'http://localhost:5000/image', true); // or https://example.com/upload/image
    xhr.send(formData);
    
};



function loadgallery(json_data, first) {
    $('#imagem').hide();
    var arr = JSON.parse(json_data.response);
    
    str = "";
    var x = 0;
    for (ke in arr){
        
        str = str + '<div class="col-lg-3 col-md-4 col-xs-6">'
            + '<input id="' + ke + 'd" name="dados" type="checkbox"\> Relevante?'
            + '<input id="' + ke + 'i" name="dados" type="checkbox"\> Irrelevante?'
            + '<a href="#" class="d-block mb-4 h-100">' + 
            '<img class="img-fluid img-thumbnail img-responsive" style="width:300px;height: 150px;" src="../corel1000/' + ke + '" alt="' + arr[ke] + '"\>'
            + "<\a> </div>";
    }
    
 
    //append the markup to the DOM
    let k = document.createRange().createContextualFragment(str);
    dados = arr;
    
    document.getElementById("formbusca").style.display="none";
    document.getElementById("imagens").style.display="block";
    document.getElementById("refilter").style.display="block";
    document.getElementById("realimagens").append(k);
};
