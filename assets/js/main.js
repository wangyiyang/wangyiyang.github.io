function toggleMenu() {
  var nav = document.getElementsByClassName("site-header-nav")[0];
  if (nav.style.display == "inline-flex") {
    nav.style.display = "none";
  } else {
    nav.style.display = "inline-flex";
  }
}

jQuery(function() {
  // 回到顶部
  function toTop () {
    var $toTop = $(".gotop");

    $(window).on("scroll", function () {
      if ($(window).scrollTop() >= $(window).height()) {
        $toTop.css("display", "block").fadeIn();
      } else {
        $toTop.fadeOut();
      }
    });

    $toTop.on("click", function (evt) {
      var $obj = $("body,html");
      $obj.animate({
        scrollTop: 0
      }, 240);

      evt.preventDefault();
    });
  }

  // 代码复制功能
  function addCodeCopyButtons() {
    // 查找所有代码块
    var codeBlocks = document.querySelectorAll('.highlight');
    
    codeBlocks.forEach(function(codeBlock) {
      // 创建复制按钮
      var copyButton = document.createElement('button');
      copyButton.className = 'code-copy-btn';
      copyButton.type = 'button';
      copyButton.setAttribute('aria-label', '复制代码');
      copyButton.innerHTML = '复制';
      
      // 将按钮添加到代码块容器
      codeBlock.appendChild(copyButton);
      
      // 添加点击事件
      copyButton.addEventListener('click', function() {
        var code = codeBlock.querySelector('code');
        var textToCopy = code ? code.innerText : codeBlock.innerText;
        
        // 使用现代 Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(textToCopy).then(function() {
            showCopySuccess(copyButton);
          }).catch(function(err) {
            console.error('复制失败:', err);
            fallbackCopyToClipboard(textToCopy, copyButton);
          });
        } else {
          // 降级方案
          fallbackCopyToClipboard(textToCopy, copyButton);
        }
      });
    });
  }
  
  // 显示复制成功状态
  function showCopySuccess(button) {
    button.classList.add('copied');
    button.innerHTML = '已复制';
    
    setTimeout(function() {
      button.classList.remove('copied');
      button.innerHTML = '复制';
    }, 2000);
  }
  
  // 降级复制方案（用于不支持现代 API 的浏览器）
  function fallbackCopyToClipboard(text, button) {
    var textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
      showCopySuccess(button);
    } catch (err) {
      console.error('降级复制方案也失败了:', err);
      button.innerHTML = '复制失败';
      setTimeout(function() {
        button.innerHTML = '复制';
      }, 2000);
    }
    
    document.body.removeChild(textArea);
  }

  toTop();
  addCodeCopyButtons();
});
