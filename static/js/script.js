var userCard = {
    wrap : '<div class="col-4">',
    begin : '<div class="card">',

    head_begin : '<div class="card-header text-center overflow-auto" Style="height:100px">',
    id_tag:'ID : ',
    id: '',
    email_tag: '<br>Email : ',
    email : '',
    head_end : '</div>',
    
    body_begin : '<div class="card-body text-center overflow-auto" Style="height:150px">',
    fname_tag:'First Name : ',
    first_name : '' ,
    lname_tag:'<br>Last Name : ',
    last_name : '' ,
    address_tag:'<br>Address : ',
    address : '',
    auth_tag : '<br>Authorization : ',
    authorization : '',
    body_end : '</div>',
    

    foot_begin : '<div class="card-footer text-center">',
    edit_btn:'<button type="button" class="btn btn-success"',
    edit_btn_onclick : 'onclick="editItem(',
    edit_btn_onclick_value:'',
    edit_btn_onclick_end : ')"',
    edit_btn_end: '>Edit</button>',
    delete_btn:'<button type="button" class="btn btn-danger"',
    delete_btn_onclick : 'onclick="deleteItem(',
    delete_btn_onclick_value:'',
    delete_btn_onclick_end : ')"',
    delete_btn_end: '>Delete</button>',
    foot_end : '</div>',

    end : '</div>',
    wrap_end : '</div>'
};
var imCard = {
    wrap : '<div class="col-4">',
    begin : '<div class="card">',

    img_begin: '<img ',
    im_src: 'src= ',
    image : '',
    img_end : 'class="card-img-top">',

    head_begin : '<div class="card-header text-center" >',
    id_tag:'ID : ',
    id: '',
    name_tage:'<br>Name : ',
    name : '' ,
    head_end : '</div>',

    body_begin : '<div class="card-body text-center overflow-auto" Style="height:150px">',
    price_tag:'Price : ',
    price : '',
    supp_tag:'<br>Supplier :  ',
    supplier : '',
    cat_tag:'<br>Category : ',
    category : '',
    brand_tag:'<br>Brand : ',
    brand : '',
    offer_tag:'<br>Offer : ',
    offer : '',
    body_end : '</div>',

    foot_begin : '<div class="card-footer text-center">',
    cc_tag:'Carts : ',
    cart_count : '',
    pc_tag:'<br>Purchases : ',
    purch_count : '',
    wlc_tag:'<br>Wishlists : ',
    wl_count : '',
    edit_btn:'<br><button type="button" class="btn btn-success"',
    edit_btn_onclick : 'onclick="editItem(',
    edit_btn_onclick_value:'',
    edit_btn_onclick_end : ')"',
    edit_btn_end: '>Edit</button>',
    delete_btn:'<button type="button" class="btn btn-danger"',
    delete_btn_onclick : 'onclick="deleteItem(',
    delete_btn_onclick_value:'',
    delete_btn_onclick_end : ')"',
    delete_btn_end: '>Delete</button>',
    foot_end : '</div>',

    end : '</div>',
    wrap_end : '</div>'
};
var orig_data = {};
const host = window.location.protocol + "//" +window.location.host;


async function fetchTable(table){
    var element = document.getElementById("resultCol");
    var url= host+'/dbfetch';
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'}, 
        body: JSON.stringify(table)
    });
    
    var y = await x.json();
    if(y['Value']===true)
    {
        if(table.toLocaleLowerCase() == 'product')
        {
            var html = "";
            for (r in y['Result'])
            {
                for(i in y['Result'][r])
                {  
                    if(i === 'image')
                    {
                        imCard[i] = JSON.stringify(y['Result'][r][i]);
                    }else
                    {
                        imCard[i] = y['Result'][r][i];
                    } 
                }
                imCard['edit_btn_onclick_value'] = "'"+table+"'"+','+imCard['id'];
                imCard['delete_btn_onclick_value'] = "'"+table+"'"+','+imCard['id'];
                for (k in imCard){html += imCard[k];}
            }
            element.innerHTML = html;
        }else if(table.toLocaleLowerCase() == 'user')
        {
            var html = "";
            for (r in y['Result'])
            {
                for(i in y['Result'][r])
                {  
                    if(i in userCard)
                    {
                        userCard[i] = y['Result'][r][i];  
                    }
                }
                userCard['edit_btn_onclick_value'] = "'"+table+"'"+','+userCard['id'];
                userCard['delete_btn_onclick_value'] = "'"+table+"'"+','+userCard['id'];
                for (k in userCard){html += userCard[k];}
            }
            element.innerHTML = html;
            
        }else
        {
            var container = document.createElement('div');
            container.className = "col-8 card" ;
            var ul = document.createElement('ul');
            ul.className = "list-group list-group-flush";
            for(i in y['Result'])
            {   
                var item = document.createElement('li');
                item.className = "list-group-item d-flex justify-content-between align-items-start";
                var vrule = document.createElement('div');
                vrule.className = "vr";
                for(r in y['Result'][i])
                {
                    item.innerHTML += r + ' : ' +  y['Result'][i][r];
                    item.appendChild(vrule);
                }
                var cont2 = document.createElement('div');
                var edit_btn = document.createElement('a');
                edit_btn.href = '#';
                edit_btn.innerHTML = 'Edit';
                edit_btn.setAttribute('onclick',`editItem('${table}',${y["Result"][i]["id"]})`);
                var delete_btn = document.createElement('a');
                delete_btn.href = '#';
                delete_btn.className = "text-danger";
                delete_btn.innerHTML = 'Delete';
                delete_btn.setAttribute('onclick',`deleteItem('${table}',${y["Result"][i]["id"]})`);
                cont2.append(edit_btn,vrule,delete_btn);
                item.appendChild(cont2)
                ul.appendChild(item);
            }
            container.replaceChildren(ul);
            element.replaceChildren(container);
        }
            
        

    }else if(y['Value']==401)
    {
        location.reload(true);
    }
    else
    {
        alertMsg(y,document.getElementById('insertAlert'))
    }
    
}
async function deleteItem(table,id)
{
    var auth = await tokenAuth();
    if (auth===true){
        var confirmation = await confirmDialog("Confirm Delete");
        if(confirmation);
        {
            var url= host+'/dbdelete/'+id;
            var x = await fetch(url,{
                method: 'POST',
                headers: {'Content-Type':'application/x-www-form-urlencoded'},
                body: JSON.stringify(table)
            });
            var result = await x.json();
            if(result['Value']===true || result['Value']===false)
            {
                alertMsg(result,document.getElementById("insertAlert"));
                fetchTable(table);
            }
            else if(result['Value']==401)
            {
                location.reload(true);
            }
        }
    }else
    {
        location.reload(true);
    }
     
}
function confirmDialog(msg) 
{
    return new Promise(function (resolve, reject) {
      let confirmed = window.confirm(msg);
  
      return confirmed ? resolve(true) : reject(false);
    });
}
async function editItem(table,id)

{   
    var result = await getById(table,id);
    orig_data = result['Result']
    if (result['Value'])
    {
        await getForm(table,false,id).then(() => addContentToForm(orig_data));
    }
}
function addContentToForm(content)
{
    var form = document.getElementById("addNewForm");
    var form_elements = form.elements;
    for (i = 0; i < form.length; i++) 
    {
        elem = form_elements[i].name.toLocaleLowerCase();
        
        if(JSON.stringify(content[elem]))
        {   
            form_elements[i].value = content[elem];   
        }
    }
  
}
async function updateById(table,id)
{
    var form = document.getElementById("addNewForm");
    var form_elements = form.elements;
    var formData = new FormData(form);
    formData.append('table', table);
    for (i = 0; i < form.length; i++) 
    {
        elem = form_elements[i].name.toLocaleLowerCase();
        if((orig_data[elem] == formData.get(elem) || !Boolean(form_elements[i].value)) && orig_data[elem])
        {   
            formData.delete(elem); 
        }
    }
    if(Boolean(formData.get('image'))){formData.append('origImage',orig_data['image']);}
    var count = 0;
    for(var val of formData.keys()){count++;}
    if(count == 1)
    {
        alertMsg({'Value':false,'Message':'No updates'},document.getElementById("insertAlert"));
    }
    else
    {
        var url= host + '/dbinsert/' + id;
        var x = await fetch(url,{
            method: 'POST', 
            body: formData
        });
        result =  await x.json();
        if(result['Value']===true || result['Value']===false)
        {
            alertMsg(result,document.getElementById("insertAlert"));
            resetInputForm();
            fetchTable(table);
        }else if(result['Value']==401)
        {
            location.reload(true);
        }
    }
    
    

}
async function getById(table,id)
{   
    var url= host + '/dbfetch/' + id;
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'}, 
        body: JSON.stringify(table)
    });
    var result = await x.json();
    if(result['Value']===true)
    {
        return result
    }else if(result['Value']==401)
    {
        location.reload(true);
        return Promise.reject(false);
    }else
    {
        alert(result,document.getById('insertAlert'));
        return Promise.reject(false);
    }
}
function resetInputForm()
{
    document.getElementById("newFormContent").innerHTML ="";
    var header = document.getElementById("formHeader");
    header.innerHTML= "";
    header.style.display = "none";
    var button = document.getElementById("form-submit-btn");
    button.setAttribute('onclick','');
    button.style.display = "none";

}
async function getForm(value,newForm=true,id=null)
{   
    var form = document.getElementById("addNewForm");
    var content = document.getElementById("newFormContent");
    var url= host + '/form';
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: JSON.stringify(value)
    });
    var y = await x.json();
    if(y['Value']===true)
    {
        content.innerHTML = y['Result']['body'];  
        
        var form_elements = form.elements;
        var header = document.getElementById("formHeader");
        header.innerText = value;
        header.style.display = 'inline-block';
        var select = [];
        for (i = 0; i < form.length; i++) 
        {
            if (form_elements[i].nodeName.toLocaleLowerCase() === "select")
            {   
            select.push(getList(form_elements[i].name.toLocaleLowerCase()));
            
            }
            else if(form_elements[i].nodeName.toLocaleLowerCase() === "button") 
            {
                var button = form_elements[i];
                form_elements[i].style.display = "inline-block";
            }
        }
        
        
        if(newForm){
            button.setAttribute('onclick',`insertIntoTable('${value}')`);
            button.innerHTML = 'Insert';
        }else{

            button.setAttribute('onclick',`updateById('${value}',${id})`);
            button.innerHTML = 'Update';
        }
        await Promise.all(select);
    }else if(y['Value']==401)
    {
        location.reload(true);
    }
    
}
async function getList(value)
{   
    var element = document.getElementById(value+"DropDown");
    var url= host + '/dbfetch';
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: JSON.stringify(value)
    });
    var y = await x.json();
    if(y['Value']===true)
    {
        var content = y['Result'];
        for(i=0; i<content.length;i++)
        {
            var keys = [];
            for(j in content[i]){keys.push(j);}
            var opt = document.createElement('option');
            opt.value = content[i][keys[0]];
            if(value.toLocaleLowerCase()=='offer')
            {
                opt.innerText = content[i][keys[1]]+' - '+content[i][keys[2]]+'%';
            }else{opt.innerHTML = content[i][keys[1]];}
            
            element.appendChild(opt);

        }
        
        return Promise.resolve(true);
    } 
    else if(y['Value']==401)
    {
        location.reload(true);
        return Promise.reject(false);
    }
    else
    {   
        alert(y,document.getById('insertAlert'));
        return Promise.reject(false);
    }
    
}
async function tokenAuth()
{
    var url= host + '/tokenauth';
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'}
    });
    var result =  await x.json();
    if(result['Value']===true)
    {
        return Promise.resolve(true);
    }else if(result['Value']==401)
    {
        return Promise.reject(false);
    }
}
async function insertIntoTable(table)
{   
    var auth = await tokenAuth();
    if(auth === true)
    {
        var form = document.getElementById("addNewForm");
        var formData = new FormData(form);
        var flag = true
        formData.append('table',table);
        for(var i of formData.values())
        {
            if(i instanceof File)
            {
                if(!Boolean(i.name))
                {
                    flag = false;
                }
            }
            else
            {
                if(!Boolean(i.length))
                {
                    flag = false;
                }
            }
        }
        if(flag){    
            var url= host + '/dbinsert';
            var x = await fetch(url,{
                method: 'POST',
                body: formData
            });
            var result =  await x.json();
            if(result['Value']===true || result['Value']===false)
            {
                alertMsg(result,document.getElementById("insertAlert"));
                resetInputForm();
                fetchTable(table);
            }else if(result['Value']==401)
            {
                location.reload(true);
            }
        }
        else
        {
            alertMsg({'Value':false,'Message':'Empty fields'},document.getElementById("insertAlert"))
        }
    }else
    {
        location.reload(true);
    }
}
function alertMsg(msg,alert)
{
   if (msg != null)
    {
        if (msg['Value'] == true)
        {
            alert.className = "alert alert-success" ;
        }
        else
        {
            alert.className = "alert alert-danger" ;
        }
        alert.innerText = msg['Message']
        alert.style.display = 'inline-block'
        setTimeout(() => {closeAlert(alert)}, 5000);
    }
}
function closeAlert(alert)
{
    alert.style.display = 'none';
}
function showpassword()
{
    var elem =  document.getElementById("loginPassowrd");
    if(elem.type.toLocaleLowerCase() == 'text')
    {
        elem.type = 'password';
    }else{elem.type = 'text';}
}
function logoutFormSubmit()
{
    document.getElementById('logoutForm').submit();
}
