var imCard = {
    wrap : `<div class="productCard col-3 shadow-lg" onclick="showProduct(this.id)" data-bs-toggle="modal" data-bs-target="#productModal" id = `,
    wrap_id:'',
    wrap_closing : '>',
    begin : '<div class="card">',

    img_begin: '<img ',
    im_src: 'src = ',
    image : '',
    img_end : ' class="card-img-top">',

    head_begin : '<div class="card-header gap-1 overflow-auto bg-gradient" Style="height:100px; background-color:#F9F9F9;">',
    name_tage:'<br>Name : ',
    name : '' ,
    head_end : '</div>',

    body_begin : '<div class="card-body  overflow-auto" Style="height:150px; background-color:#FFFFFF;">',
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

    // foot_begin : '<div class="card-footer text-center overflow-auto" Style="height:120px">',
    // edit_btn:'<br><button type="button" class="btn btn-success"',
    // edit_btn_onclick : 'onclick="editItem(',
    // edit_btn_onclick_value:'',
    // edit_btn_onclick_end : ')"',
    // edit_btn_end: '>Edit</button>',
    // delete_btn:'<button type="button" class="btn btn-danger"',
    // delete_btn_onclick : 'onclick="deleteItem(',
    // delete_btn_onclick_value:'',
    // delete_btn_onclick_end : ')"',
    // delete_btn_end: '>Delete</button>',
    // foot_end : '</div>',

    end : '</div>',
    wrap_end : '</div>'
};
var himCard =
{
    wrap: '<div class="card mb-3"  style="max-height:200px; id= ',
    wrap_id: '',
    wrap_closing: '">',
    row : '<div class="row g-0">',
    im_div:  '<div class="col-md-4">',
    img_begin: '<img ',
    im_src: 'src = ',
    image : '',
    img_end : ' class="img-fluid rounded-start">',      
    im_div_end: '</div>',
    begin : '<div class="col-md-8">',
    body_begin : '<div class="card-body">',
    title_begin : '<h5 class="card-title">',
    name : '',
    title_end: '</h5>',

    price_begin : '<h7 class="card-text">',
    price : '',
    price_end : '</h7><br>',
    button : '',

    body_end:  '</div>',
    end: '</div>',
    row_end : '</div>',
    wrap_end:'</div>'
};
var notifyCard={
    wrap:'<div class="card">',
    header: '<div class="card-header"> Execlusive Offer</div>',
    body:'<div class="card-body"> <p class="card-text">',
    Message:'',
    Message_end:'</p>',
    body_end:'</div>',
    wrap_end:'</div>'
};
const host = window.location.protocol + "//" +window.location.host;
var user = '';
async function data()
{
    await Promise.all([getList('Category','categories'),
                      getList('Brand','brands'),getUser(),
                      getIndexProducts('recommends', 'recommendsCol'),
                      getIndexProducts('featured', 'featuredCol'),
                      getIndexProducts('newarrival', 'arrivalCol')]);
    document.getElementById('productsLink').setAttribute('onclick',`getAllProducts()`);
}
async function getUser()
{
    var url= host + '/useroptions';
    var x = await fetch(url,{method:'POST'});
    var y = await x.json();
    if(y['Value']===true)
    {
        document.getElementById('UserDropDown').innerHTML=y['Result']['body'];
        if(y['Message'].toLocaleLowerCase()==='user')
        {
            user =  y['User']
            document.getElementById('UserName').innerHTML = user['first_name']+' '+user['last_name'];
            document.getElementById('UserEmail').innerHTML = user['email'];
        }
        
        
    }
    
}
async function appendBody(html){
    document.body.innerHTML += html
}
function showpassword(value,id)
{
    var elem =  document.getElementById(value);
    var icon =  document.getElementById(id);
    if(elem.type.toLocaleLowerCase() == 'text' && icon.className == 'bi bi-eye')
    {
        elem.type = 'password';
        icon.className = 'bi bi-eye-slash';
    }else{elem.type = 'text'; icon.className = 'bi bi-eye';}
}
async function getList(value,link)
{ 
    var element = document.getElementById(value+"DropDown");
    var url= host + '/'+link;
    var x = await fetch(url,{
        method: 'POST'
    });
    var y = await x.json();
    if(y['Value']===true)
    {
        var content = y['Result'];
        for(i=0; i<content.length;i++)
        {
            var keys = [];
            for(var j in content[i]){keys.push(j);}
            var li = document.createElement('li');
            li.style.cursor = "pointer";
            li.classList = "dropdown-item";
            li.value = content[i][keys[0]];
            li.innerHTML = content[i][keys[1]];
            li.setAttribute('onclick',`filterProducts({${value.toLowerCase()}:${content[i][keys[0]]}})`);
            element.appendChild(li);

        }
        
    } 
    else
    {
        location.reload(true);
    }

    
}
async function getAllProducts()
{   
    var element = document.getElementById('resultColInputGroup');
    var brandSelect = document.createElement('select');
    brandSelect.classList = "form-select";
    brandSelect.id = "brandSelector";
    brandSelect.innerHTML = '<option value="" selected>Brand</option>';
    var categorySelect = document.createElement('select');
    categorySelect.classList = "form-select";
    categorySelect.id = "categorySelector";
    categorySelect.innerHTML = '<option value="" selected>Category</option>';
    var brands = document.getElementById('BrandDropDown').childNodes;
    var categories = document.getElementById('CategoryDropDown').childNodes;
    var brand = '';
    element.innerHTML='';
    for (i = 1; i < brands.length; ++i)
    {
        brand = document.createElement('option');
        brand.value =  brands[i].value;
        brand.innerHTML =  brands[i].innerHTML;
        brandSelect.appendChild(brand);
    }
    for (j = 1; j < categories.length; j++)
    {
        category = document.createElement('option');
        category.value =  categories[j].value;
        category.innerHTML =  categories[j].innerHTML;
        categorySelect.appendChild(category);
    }
    element.appendChild(categorySelect);
    element.appendChild(brandSelect);
    var submitButton = document.createElement('button');
    submitButton.classList = "btn btn-primary";
    submitButton.innerHTML="Filter"
    submitButton.setAttribute('onclick',`filterProducts()`);
    element.appendChild(submitButton);
    element.style.visibility='visible'; 
    filterProducts();


}
async function filterProducts(data="")
{
    document.getElementById("indexCol").innerHTML = "";
    if(data != "")
    {
        document.getElementById("resultColInputGroup").innerHTML=''
    }
    var dict = {}
    var brand =  document.getElementById('brandSelector');
    var category = document.getElementById('categorySelector');
    
    if (brand != null)
    {
        if(brand.value != "")
        {
            dict['brand'] = brand.value
        }
    }
    if(category != null)
    {
        if(category.value!="")
        {
            dict['category'] = category.value
        }
    }
    if(Object.keys(dict).length > 0)
    {
        data = dict
    }
    var element = document.getElementById('resultCol');
    element.innerHTML=''
    var url= host + '/products';
    var x = await fetch(url,{
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'}, 
        body: JSON.stringify(data)
    });
    var y = await x.json();
    var html = "";
    if(y['Value']===true)
    {
        
        for (r in y['Result'])
        {
            imCard['wrap_id'] = JSON.stringify(y['Result'][r]['id']);
            for(i in y['Result'][r])
            {  
                if(i === 'image')
                {
                    imCard[i] = JSON.stringify(y['Result'][r][i]);
                }else
                {
                    if(i in imCard)
                    {
                        imCard[i] = y['Result'][r][i];
                    }
                } 
            }
            for (k in imCard){html += imCard[k];}
        }
        element.innerHTML = html;
    }
}
async function submitForm(route,id)
{
    var elem = '';
    var data = {};
    var form = document.getElementById(id);
    var form_elements = form.elements;
    var flag = true;
    for (i = 0; i < form.length; i++) 
    {
        elem = form_elements[i].name.toLocaleLowerCase();
        if(form_elements[i].nodeName.toLocaleLowerCase() != "button")
        {
            if(form_elements[i].value.length>0 )
            {   
                data[elem] =form_elements[i].value;   
            }else
            {
                flag = false
            }
        }
    }
    if(flag === true){
        var url= host + route;
        var x = await fetch(url,{
            method: 'POST',
            body: JSON.stringify(data)
        });
        var result =  await x.json();
        if(result['Value']===true)
        {
            location.reload(true);
        }else
        { 
            alertMsg(id+'Alert',result);
        }
    }else
    {
        alertMsg(id+'Alert',{'Value':false,'Message':'Fill All Fields'});
    }

}
function logoutFormSubmit()
{
    document.getElementById('logoutForm').submit();
    user = ''
}
async function alertMsg(id,input)
{
    var alertpopup = document.getElementById(id);
    if (input != null)
    {
        if (input['Value'] == true)
        {
            alertpopup.classList = "alert alert-success w-25 position-fixed text-center start-50 translate-middle-x" ;
        }
        else
        {
            alertpopup.classList = "alert alert-danger w-25 position-fixed text-center start-50 translate-middle-x" ;
        }
        alertpopup.innerText = input['Message'];
        alertpopup.style.visibility = 'visible';
        setTimeout(() => {closeAlert(id)}, 5000);
    }

}
function closeAlert(id)
{
    document.getElementById(id).style.visibility = 'hidden';
}
function showProduct(id)
{
    var modalBody = document.getElementById("productModalBody");
    var productCard = document.getElementById(id);
    productCard.classList.remove('productCard');
    modalBody.innerHTML = productCard.innerHTML+'<i class="bi bi-x-lg position-absolute end-0" data-bs-dismiss="modal" aria-label="Close"></i>';
    var containter = document.createElement('div');
    containter.classList ='sticky-bottom';
    var cartGroup = document.createElement('div');
    cartGroup.classList = 'input-group w-50 position-absolute end-0';
    cartGroup.style.padding='2px';
    var wishListGroup = document.createElement('div');
    wishListGroup.classList = 'input-group w-50 position-absolute start-0';
    wishListGroup.style.padding='2px';
    var inputNumber = document.createElement('input');
    inputNumber.type = 'number';
    inputNumber.classList = 'form-control';
    inputNumber.name = 'quantity';
    inputNumber.placeholder = 'QTY';
    inputNumber.id = 'quantityInput';
    var addCartButton = document.createElement('span');
    addCartButton.setAttribute('onclick',`addToCart('addcartitem',${id})`);
    addCartButton.classList = 'input-group-text bi bi-cart-plus-fill';
    addCartButton.id = 'addToCartButton'; 
    var addWLButton = document.createElement('span');
    addWLButton.setAttribute('onclick',`addToWishList(${id})`);
    addWLButton.classList = 'input-group-text bi bi-bag-heart-fill';
    var alertMsg = document.createElement('div');
    alertMsg.id = "productAlert";
    alertMsg.role = "alert";
    alertMsg.style.visibility = "hidden"; 
    wishListGroup.appendChild(addWLButton);
    cartGroup.appendChild(inputNumber);
    cartGroup.appendChild(addCartButton);
    containter.append(cartGroup);
    containter.append(wishListGroup);
    modalBody.appendChild(alertMsg);
    modalBody.appendChild(containter);
    productCard.classList.add('productCard');
}
function clickSignin()
{
    document.getElementById("signinButton").click();
}
function clickSignup()
{
    document.getElementById("signupButton").click();
}
async function getListItems(link)
{
    var element = document.getElementById("productModalBody");
    element.innerHTML='';
    var deleteButton = '';
    var url= host + '/'+link;
    var x = await fetch(url,{method: 'POST'});
    var y = await x.json();
    var html = "";
    if(y['Value']===true)
    {
        
        for (r in y['Result'])
        {
            himCard['wrap_id'] = JSON.stringify(y['Result'][r]['id']);
            for(i in y['Result'][r])
            {   
                if(i === 'image')
                {
                    himCard[i] = JSON.stringify(y['Result'][r][i]);
                }else
                {
                    if(i in himCard)
                    {
                        himCard[i] = y['Result'][r][i];
                    }
                } 
            }
            if(link.toLocaleLowerCase()==='wishlistitems')
            {
                deleteButton = '<div class="input-group w-100 justify-content-end"><span class="input-group-text bi bi-heartbreak-fill" onclick="deleteItem(\'deletewishlistitem\',\''
                                + y["Result"][r]["id"] + '\')"></span></div>';
            }
            else
            {
                deleteButton = '<div class="input-group w-100 "><input type="number" class="form-control" '
                +'name="quantity" placeholder="'+y['Result'][r]['quantity']+'" id="quantityInput"> '
                +'<span class="input-group-text bi bi bi-cart-plus" onclick="addToCart(\'updatecartitem\',\''+y["Result"][r]["id"] + '\')"></span>'
                +'<span class="input-group-text bi bi-cart-dash-fill" onclick="deleteItem(\'deletecartitem\',\''
                +y["Result"][r]["id"] + '\')"></span></div>';
            }
            himCard['button'] = deleteButton;
            for (k in himCard){html += himCard[k];}
        }
        element.innerHTML = html+'<i class="bi bi-x-lg position-absolute end-0" id="closeProductModal" data-bs-dismiss="modal" aria-label="Close"></i>';
    }else
    {
        if(y['Message'].toLocaleLowerCase()==='unauthorized')
        {
            location.reload(true);
        }
        element.innerHTML = '<i class="bi bi-x-lg position-absolute end-0" id="closeProductModal" data-bs-dismiss="modal" aria-label="Close"></i>';
        alertMsg('mainAlert',y)
    }
}
async function addToCart(link,id)
{   
    if(user != ''){
        var quantity = document.getElementById('quantityInput').value;
        var data = {'prod_id':id,'quantity':quantity};
        var url= host + '/'+link;
        var x = await fetch(url,{
            method: 'POST',
            body: JSON.stringify(data)
        });
        var y = await x.json();
        if(y['Value']===false)
        {
            if (y['Message'].toLocaleLowerCase()==='unauthorized')
            {
                if(user != ''){user='';logoutFormSubmit();}
                
            }
            else{alertMsg('productAlert',y);}
        }else
        {
            alertMsg('productAlert',y);
        }
    }
    else
    {
        clickSignin();
    }
}
async function addToWishList(id)
{   
    if(user != ''){
        var data = {'prod_id':id};
        var url= host + '/addwishlistitem';
        var x = await fetch(url,{
            method: 'POST',
            body: JSON.stringify(data)
        });
        var y = await x.json();
        
        if(y['Value']===false)
        {
            if (y['Message'].toLocaleLowerCase()==='unauthorized')
            {

                if(user != ''){user='';logoutFormSubmit();}
               
            }
            else{alertMsg('productAlert',y);}
        }else
        {
            alertMsg('productAlert',y);
        }
    }else
    {
        clickSignin();
    }

}
async function deleteItem(link,id)
{

    var data = {'prod_id':id};
    var url= host + '/'+link;
    var x = await fetch(url,{
        method: 'POST',
        body: JSON.stringify(data)
    });
    var y = await x.json();

    if(y['Value']===false)
    {
        if (y['Message'].toLocaleLowerCase()==='unauthorized')
        {
            if(user != ''){user='';logoutFormSubmit();}
        }
        else{alertMsg('mainAlert',y);}
    }else
    {
        alertMsg('mainAlert',y);
        location.reload(true);
    }
}

function closeModal()
{
    document.getElementById('closeProductModal').click();
}
async function getNotifications()
{
    var element = document.getElementById("productModalBody");
    element.innerHTML='';
    var url= host + '/notifications';
    var x = await fetch(url,{method: 'POST'});
    var y = await x.json();
    var html = "";
    if(y['Value']===true)
    {
        for(var i in y['Result'])
        {   
            notifyCard['Message'] = y['Result'][i]['message'];
            for (k in notifyCard){html += notifyCard[k];}
        }
        element.innerHTML = html+'<i class="bi bi-x-lg position-absolute end-0" id="closeProductModal" data-bs-dismiss="modal" aria-label="Close"></i>';
    }
    else
    {
        if(y['Message'].toLocaleLowerCase()==='unauthorized')
        {
            if(user != ''){user='';logoutFormSubmit();}
            
        }
        
        element.innerHTML = '<i class="bi bi-x-lg position-absolute end-0" id="closeProductModal" data-bs-dismiss="modal" aria-label="Close"></i>';
        alertMsg('mainAlert',y)
        
        
    }    

}
async function getIndexProducts(link, col)
{
    
    var element = document.getElementById(col);
    var url= host + '/'+link;
    var x = await fetch(url,{method: 'POST'});
    var y = await x.json();
    var html = "";
    if(y['Value']===true)
    {
        for (r in y['Result'])
        {
            imCard['wrap_id'] = JSON.stringify(y['Result'][r]['id']);
            for(i in y['Result'][r])
            {  
                if(i === 'image')
                {
                    imCard[i] = JSON.stringify(y['Result'][r][i]);
                }else
                {
                    if(i in imCard)
                    {
                        imCard[i] = y['Result'][r][i];
                    }
                } 
            }
            for (k in imCard){html += imCard[k];}
        }
        element.innerHTML = html;
    }
    
}