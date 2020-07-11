#前端

## UI框架
采用了`material design`中的`material kit UI`[框架](https://www.bootcdn.cn/material-kit/) ，这里使用稳定、快速、免费的前端开源项目CDN加速服务，只需要在`html`文件的`header`中引入
```html
<link href="https://cdn.bootcdn.net/ajax/libs/material-kit/2.0.6/css/material-kit.min.css" rel="stylesheet">
```
布局样式的文档参考[`material kit`](https://demos.creative-tim.com/material-kit/docs/2.0/getting-started/introduction.html)

## Jquery
引入`Jquery`主要是完成一些`ajax`请求以及`html`样式修改。

在用户注册时，当用户输入想要注册的用户名后，会向后台发送`ajax`请求，判断用户是否存在。
```javascript
$("#username").blur(function () {
    var name = $("#username").val();
    if (name) {
        $.ajax({
            url: "/everbook/examine/username",
            type: "post",
            data: {
                "name": name
            },
            success: function (result) {
                if (result.code === 1) {
                    // 用户名已存在
                    Swal.fire({
                        type: 'warning',
                        text: '用户名已存在',
                    });
                    setTimeout(function () {
                        location.reload()
                    }, 2000);
                }
            }
        });
    }
});
```
同理也可以判断邮箱是否被注册。

## Cookie
当用户登录时，`fastapi`会保留登录的`cookie`，此时前端需要对`cookie`进行简单判断，从而判断用户是否登录。

这里需要引入`jquery`中的`cookie`插件
```html
<script src="https://cdn.bootcdn.net/ajax/libs/jquery-cookie/1.4.1/jquery.cookie.min.js"></script>
```
当用户执行注销操作时，会清除浏览器的`cookie`
```javascript
function logout() {
    $.removeCookie('login_status', null);
    $.removeCookie('username', null);
    $.removeCookie('email', null);
    window.location.href = "/";
}
```
另外，登录成功后跳转至首页，需要在首页进行判断，判断加载`html`文件时是否存在登录`cookie`
```javascript
$(document).ready(function () {
    if ($.cookie("login_status") !== null && window.location.pathname !== "/") {
        window.location.href = "/";
    }
})
```

## sweetalert2
为了美观，引入了`sweetalert2`插件，代替了浏览器自带的`alert`弹窗，只需要在`header`中引用
```html
<link href="https://cdn.bootcdn.net/ajax/libs/limonte-sweetalert2/8.11.8/sweetalert2.min.css" rel="stylesheet">
<script src="https://cdn.bootcdn.net/ajax/libs/limonte-sweetalert2/8.11.8/sweetalert2.min.js"></script>
```
然后在`<script>`标签中使用
```javascript
Swal.fire({
    type: 'success',
    text: '使用成功',
});
```
关于`sweetalert2`的更多参数定义见[官方文档](https://sweetalert2.github.io/)