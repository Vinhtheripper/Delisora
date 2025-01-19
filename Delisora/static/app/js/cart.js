if (typeof csrftoken === 'undefined') {
    var csrftoken = getCookie('csrftoken');
}
console.log('CSRF Token:', csrftoken);

var updateBtns = document.getElementsByClassName('update-cart');

for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function (event) {
        event.preventDefault();

        var productId = this.dataset.product;
        var action = this.dataset.action;

        if (!productId || !action) {
            console.error('Missing productId or action data attribute');
            return;
        }

        console.log('productId:', productId, 'action:', action);
        console.log('user:', typeof user !== 'undefined' ? user : 'AnonymousUser');

        updateUserOrder(productId, action, this);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateUserOrder(productId, action, element) {
    console.log('Sending request to update cart');
    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        console.log('Response data:', data);

        if (action === 'delete') {
            // Xóa hàng khỏi bảng mà không reload trang
            const productRow = element.closest('tr');
            if (productRow) {
                productRow.remove();
            }
        } else {
            // Reload trang để cập nhật số lượng và tổng tiền
            location.reload();
        }
    })
    .catch((error) => {
        console.error('Error updating cart:', error);
        alert('Could not update cart. Please try again later.');
    });
}
