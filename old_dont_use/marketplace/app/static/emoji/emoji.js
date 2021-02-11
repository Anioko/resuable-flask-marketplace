if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}
function EmojiPicker(selector) {
    self = this;
    this.initalized = false;
    this.selector = selector;
    this.active = 'people';
    this.activateTab = function (tab){
        $('.Hema-Emoji-Picker-Tab').removeClass('active');
        $('div.Hema-Emoji-Picker-Tab[name="'+tab+'"]').addClass('active');
        $('.Hema-Emoji-Picker-Cats>li').removeClass('active');
        $('div.Hema-Emoji-Picker-Cats>li[name="'+tab+'"]').addClass('active');
        $(document).ready(function () {
            $('.Hema-Emoji-Picker-Tab.active:not(".initalized")>span').each(function () {
                    let code = parseInt($(this).attr('content'), 16);
                    $(this).html(emojione.toImage(String.fromCodePoint(code)));
                }
            );
            $('.Hema-Emoji-Picker-Tab.active').addClass('initalized');
        });
    };
    this.activateTabInit = function (tab, api){
        setTimeout(function() { api.hide();setTimeout(function () {api.show();
            $('.Hema-Emoji-Picker-Tab').removeClass('active');
            $('div.Hema-Emoji-Picker-Tab[name="'+tab+'"]').addClass('active');
            $('.Hema-Emoji-Picker-Cats>li').removeClass('active');
            $('div.Hema-Emoji-Picker-Cats>li[name="'+tab+'"]').addClass('active');
            $(document).ready(function () {
                $('.Hema-Emoji-Picker-Tab.active:not(".initalized")>span').each(function () {
                        let code = parseInt($(this).attr('content'), 16);
                        $(this).html(emojione.toImage(String.fromCodePoint(code)));
                    }
                );
                $('.Hema-Emoji-Picker-Tab.active').addClass('initalized');
                $('.Hema-Emoji-Picker-Cats>ul>li').click(function() {
                    self.activateTab($(this).attr('name'))
                });
                $('.Hema-Emoji-Picker-Tab>span').click(function(){
                    let s = $(self.selector);
                    let n = s.attr('name');
                    $('input[name="'+n+'"]').val($('input[name="'+n+'"]').val() + $(this).attr('code'));
                    s.find('.Hema-Emoji-Picker-Input').append( $(this).html());
                    $('input[name="'+n+'"]').trigger('change');
                })
            })

        }, 200);}, 200);
    };
    this.json = [];
    this.init = function () {
        let s = $(self.selector);
        if (! s.length){
            throw "Element " + self.selector + " Not Found";
        }
        if (! s.hasClass('Hema-Emoji-Picker')){
            s.addClass('Hema-Emoji-Picker');
        }
        template = '<div contenteditable="true" class="Hema-Emoji-Picker-Input"></div>'+
            '<a href="#" class="Hema-Emoji-Picker-Toggle">&#128578;</a>';
        s.html(template);
        let input = s.find('.Hema-Emoji-Picker-Input');
        let toggle = s.find('.Hema-Emoji-Picker-Toggle');
        let ih = input.height();
        let tw = toggle.width();
        let th = tw - ih;
        toggle.css('font-size', 20);
        toggle.css('margin-left', -30);
        let emojis = '<div class="Hema-Emoji-Picker-Container">';
        let cats = '<div class="Hema-Emoji-Picker-Cats"><ul>';
        let e =  emojione;
        e.emojiSize = 64;
        for (let i=0; i < json.length; i++){
            cats += '<li name="'+json[i].category+'">'+json[i].elems[0].code_decimal+'</li>'
            emojis += '<div name="'+json[i].category+'" class="Hema-Emoji-Picker-Tab">';
            for (let j=0; j<json[i].elems.length;j++){
                emojis+='<span code="'+json[i].elems[j].code_decimal+'" content="'+json[i].elems[j].unicode+'">'+json[i].elems[j].code_decimal+'</span>'
            }
            emojis += '</div>'
        }
        cats += '</ul>';
        emojis += cats + '</div>';

        $(toggle).qtip({
            content: {
                text: emojis,
            },
            show: 'click',
            hide: 'click',
            position: {
                my: 'bottom left',  // Position my top left...
                at: 'top right', // at the bottom right of...
                target: $(self.selector) // my target
            }
        });
        let api = $(toggle).qtip('api');
        $(toggle).click(function () {
            if (self.initalized == false){
                self.activateTabInit('people', api);
                self.initalized = true;
            }
        });

    };
    fetch("/static/emoji/cats.json")
        .then(response => response.json())
        .then(function (json) {
                self.json = json;
                self.init();
            }
        );
}
// $(document).on('click', '.Hema-Emoji-Picker-Toggle', function () {
//
// });
// fetch("codes.json")
//     .then(response => response.json())
//     .then(function (json) {
//             let cats = [];
//             new_json = [];
//             for (let i=0; i < Object.keys(json).length; i++){
//                 let new_elem = {};
//                 let k = Object.keys(json)[i];
//                 new_elem.key = k;
//                 new_elem.unicode= json[k].unicode;
//                 new_elem.unicode_alt= json[k].unicode_alt;
//                 new_elem.code_decimal= json[k].code_decimal;
//                 new_elem.name= json[k].name;
//                 new_elem.shortname= json[k].shortname;
//                 new_elem.category= json[k].category;
//                 new_elem.emoji_order= json[k].emoji_order;
//                 new_elem.aliases= json[k].aliases;
//                 new_elem.aliases_ascii= json[k].aliases_ascii;
//                 new_elem.keywords = json[k].keywords;
//                 if (! cats.includes(json[k].category)){
//                     cats.push(json[k].category);
//                 }
//                 new_json.push(new_elem)
//             }
//             console.log(cats);
//             console.log(new_json.length, cats.length);
//             result = [];
//             for (let i = 0; i < cats.length; i++){
//                 let elems = new_json.filter(row => row.category == cats[i]);
//                 console.log(elems);
//                 result.push({"category": cats[i], elems: elems});
//             }
//             console.log(result.length);
//             $('#content').html(JSON.stringify(result));
//         }
//     );