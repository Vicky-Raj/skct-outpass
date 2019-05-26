function logout(){
    swal({
    title: "Are you sure?",
    text: "Are you sure you want to log out?",
    icon: "warning",
    buttons: true,
    dangerMode: true,
  })
  .then((willDelete) => {
    if (willDelete) {
      window.location.href = window.location.protocol + '//'+
      window.location.hostname + ':' + window.location.port+ 
      '/logout/';
    } 
  });
}