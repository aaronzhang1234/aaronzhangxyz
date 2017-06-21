function deleteGroup(){
    if(confirm("Are you sure you want to delete this group? This is irreversible.")==true){
    }else{
        event.preventDefault();
    }
}
function deleteAccount(){
    if(confirm("Are you sure you want to delete this account?\nThis is irreversible. All groups you lead will also be deleted")==true){

    }else{
        event.preventDefault();
    }
}
