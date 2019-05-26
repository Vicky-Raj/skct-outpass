function accept(pk){
    var url = window.location.protocol+'//'+window.location.hostname+':'+window.location.port+'/tutor/outpass/accept/';
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.onload = ()=>{
        if(request.status == 200){
            var response = JSON.parse(request.responseText);
            if(response['accepted']){
                window.location.reload();
            } 
        }
    };
    request.send(JSON.stringify({'pk':pk}));
}

function reject(pk){
    var url = window.location.protocol+'//'+window.location.hostname+':'+window.location.port+'/tutor/outpass/reject/';
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.onload = ()=>{
        if(request.status == 200){
            var response = JSON.parse(request.responseText);
            if(response['rejected']){
                window.location.reload();
            } 
        }
    };
    request.send(JSON.stringify({'pk':pk}));
}