function del(pk){
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to cancel outpass?",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      })
      .then((willDelete) => {
        if (willDelete) {
            perm_del(pk);
        } 
      });
}



function perm_del(pk){
    var url = window.location.protocol+'//'+window.location.hostname+':'+window.location.port+'/student/outpass/delete/';
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.onload = ()=>{
        if(request.status == 200){
            var response = JSON.parse(request.responseText);
            if(response['deleted']){
                window.location.reload();
            } 
        }
    };
    request.send(JSON.stringify({'pk':pk}));

}
function create_otp(pk){
    var url = window.location.protocol+'//'+window.location.hostname+ ':' +window.location.port+ '/student/otp/gen/';
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.onload = ()=>{
        if(request.status == 200){
            var response = JSON.parse(request.responseText);
            if(response['created']){
                window.location.reload();
            }
        }
    };
    request.send(JSON.stringify({'pk':pk}));
}