const form_dark = document.querySelector(".dark"), form_light = document.querySelector(".light")
const changeBtn_dark = document.getElementById("changeBtn_dark")
const changeBtn_light = document.getElementById("changeBtn_light")

const SHOWING_CH = "showing";
const NOSHOWING_CH = "noshowing";

function selectTheme(theme){
    if(theme != "dark"){
        form_dark.classList.add(NOSHOWING_CH);
        form_dark.classList.remove(SHOWING_CH);
        form_light.classList.remove(NOSHOWING_CH);
        form_light.classList.add(SHOWING_CH);
    }
    else{
        form_dark.classList.add(SHOWING_CH);
        form_dark.classList.remove(NOSHOWING_CH);
        form_light.classList.remove(SHOWING_CH);
        form_light.classList.add(NOSHOWING_CH);
    }
}

function onMounted(){
    theme = document.documentElement.dataset.theme
    return theme
};

function changeTheme(e){
    theme = onMounted()
    console.log(theme)
    selectTheme(theme)
    document.documentElement.dataset.theme = "light"
}

function changeTheme2(e){
    theme = onMounted()
    console.log(theme)
    selectTheme(theme)
    document.documentElement.dataset.theme = "dark"
}

function init(){
    theme = onMounted()
    if(theme === "dark"){
        changeBtn_light.addEventListener("click", changeTheme)
    }
    changeBtn_dark.addEventListener("click", changeTheme2)
}


init();