//alert('Hola Mundo!!!');
const btnDelete= document.querySelectorAll('.btn-delete')

if(btnDelete){
    const btnArray=Array.from(btnDelete);
    btnArray.forEach((btn, i) => {
        btn.addEventListener('click',(e) => {
            if(!confirm('Confirme que se desea eliminar este registro')){
                e.preventDefault();
            }
        });
    });
}