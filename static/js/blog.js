function setPostsCalendarDate() {
  const postsCreated = [ ...document.getElementsByClassName('post-created-utc-string')];
  postsCreated.forEach(date => {
    date.innerHTML = moment.utc(date.innerHTML).local().calendar();
  });
}

function fadeOutAlerts() {
  $(function() {
    $('.alert').delay(0).fadeIn('normal', function() {
      $(this).delay(2500).fadeOut();
    });
  });
}


function handleStickNav(navbar, navbarBrands, stickyThreshold) {
  if (window.pageYOffset >= stickyThreshold) {
    navbar.classList.add('sticky-navbar');
    navbarBrands.forEach(elem => elem.style.display = 'flex');
  } else {
    navbar.classList.remove('sticky-navbar');
    navbarBrands.forEach(elem => elem.style.display = 'none');
  }
}

// Fire after the DOM has loaded
setTimeout(() => {
  const navbar = document.getElementById('navbar');
  const navbarBrands = [...document.getElementsByClassName('navbar-brand')];
  const stickyThreshold = navbar.offsetTop;
  window.onscroll = function() { handleStickNav(navbar, navbarBrands, stickyThreshold) };

  fadeOutAlerts()

  setPostsCalendarDate();
}, 0);