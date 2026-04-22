'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {".git/COMMIT_EDITMSG": "20062fcacc48dc885457300f29c222e0",
".git/config": "56ee6356521b12761d168a13749afe0a",
".git/description": "a0a7c3fff21f2aea3cfa1d0316dd816c",
".git/HEAD": "cf7dd3ce51958c5f13fece957cc417fb",
".git/hooks/applypatch-msg.sample": "ce562e08d8098926a3862fc6e7905199",
".git/hooks/commit-msg.sample": "579a3c1e12a1e74a98169175fb913012",
".git/hooks/fsmonitor-watchman.sample": "a0b2633a2c8e97501610bd3f73da66fc",
".git/hooks/post-update.sample": "2b7ea5cee3c49ff53d41e00785eb974c",
".git/hooks/pre-applypatch.sample": "054f9ffb8bfe04a599751cc757226dda",
".git/hooks/pre-commit.sample": "5029bfab85b1c39281aa9697379ea444",
".git/hooks/pre-merge-commit.sample": "39cb268e2a85d436b9eb6f47614c3cbc",
".git/hooks/pre-push.sample": "2c642152299a94e05ea26eae11993b13",
".git/hooks/pre-rebase.sample": "56e45f2bcbc8226d2b4200f7c46371bf",
".git/hooks/pre-receive.sample": "2ad18ec82c20af7b5926ed9cea6aeedd",
".git/hooks/prepare-commit-msg.sample": "2b5c047bdb474555e1787db32b2d2fc5",
".git/hooks/push-to-checkout.sample": "c7ab00c7784efeadad3ae9b228d4b4db",
".git/hooks/sendemail-validate.sample": "4d67df3a8d5c98cb8565c07e42be0b04",
".git/hooks/update.sample": "647ae13c682f7827c22f5fc08a03674e",
".git/index": "59912145a610db4cc2034df2695d71f2",
".git/info/exclude": "036208b4a1ab4a235d75c181e685e5a3",
".git/logs/HEAD": "afc3cdbc19abba49893fb1cf6aee7ba8",
".git/logs/refs/heads/main": "7aeea5b2a389915d874c2e392ec25271",
".git/logs/refs/remotes/origin/main": "d29f8123f222324b91df913036782ba0",
".git/objects/00/faea0a457b2c3cdc8cb39f2deba3b661aa2a77": "0cb73d543dff2eb52714879ffc59ebb6",
".git/objects/08/27c17254fd3959af211aaf91a82d3b9a804c2f": "360dc8df65dabbf4e7f858711c46cc09",
".git/objects/0b/5432b941dae97e65545150a5ad74415500c373": "77ded6d664f39306b647611dedbf2ff5",
".git/objects/0c/ea68a75e1aaf7a2c7d332e91b28068c103a67e": "24c25eccf457153679357d5149665450",
".git/objects/13/183aa61c63e8308193b28974350cf37d42898e": "ee921d052b5f20c467cf84c8a092bcd3",
".git/objects/13/9acbf2ad368737661a357c08b527a0ccb9865e": "e5fa35700282c652d6f1727c73110f3a",
".git/objects/15/d83b0a9d8dcfa19210d4ff8350550e099a4c8e": "60c1d7b2d54f1c2a8bd9d418b67fa512",
".git/objects/17/bac4b2bb0eaac89b0942bdb1cb7151d870b6b7": "0c8a3664cef738256b4732ef50f1e97e",
".git/objects/1a/4baf536d705b9c814847cb7a708a0e63d5b976": "2fb2d1d35f11fddbc0c198576152624f",
".git/objects/1b/59edf00659a3c3218b7b6c63d790e8ee54a97a": "479235b665dba6f136ee1b8f856456dc",
".git/objects/1b/694d5f06e9b8aefff8e17348f37acbff7122f1": "c4f1e9c00d20d2b949c00edd2d44d641",
".git/objects/1e/9c1e1f0537da4ec0658a3fbd8828202c567fcf": "4f703000ec1efa25b8d6d516c8f096bc",
".git/objects/27/e667bfa541fb82363f5e98a83e35562902941b": "e7d3f11ebb9ec738f4eb8930409bb79e",
".git/objects/29/5f8b8adc8db83d09f9f6300ecc6bc7e0039209": "78e35b7d5e9bf1c9cd4f203991e09b31",
".git/objects/29/7d3faa0bfba2c4deb70b89bb3203ca55b50f75": "f82fc30b1a8f6ac5dc581fa4a3140187",
".git/objects/2b/d638e7ce6e9f0491b7488567598790cef56873": "d2e546906aaf991055ba3b8ea9780f5c",
".git/objects/2c/7f236113d8bf69f86d7cf604d75c8dfe367410": "0b4141d1e6511f598df21a27ff5f9149",
".git/objects/2d/554f7c7ceac4c8e8b167046c1b0d11063dfc82": "4282d8c300f0bbec0d86e9cd2d26d9c2",
".git/objects/33/e6d7f3fd3b87e733e36876d605eb75c5967026": "f2b46028025d3111eca72fc8f8dd06ed",
".git/objects/37/e3a02178d786b0061f01a3cdd67b99aa06f1e0": "3a090fff40e1439c4d696d70bb076fc5",
".git/objects/38/e4323bb677d4b98b6a3da569d6cfeeb644caf4": "62eaca7d28f97ddef71dc68c8a3711c6",
".git/objects/3a/8cda5335b4b2a108123194b84df133bac91b23": "1636ee51263ed072c69e4e3b8d14f339",
".git/objects/3b/b8a71086ab65cb4dbe9e6e0297ba600fd69121": "95ddce8e9b3336b971c6d2a6c78a1f30",
".git/objects/45/7faa637f306ffe4a3ad56a857da93030d9dd43": "4ad9ddaaaa2bab249c63ff4d045fdb7b",
".git/objects/46/4ab5882a2234c39b1a4dbad5feba0954478155": "2e52a767dc04391de7b4d0beb32e7fc4",
".git/objects/47/3ae7a725c1d8d6224e433c0e3b28c5fc0538a4": "d198650f581aa32627b680e7c79e1449",
".git/objects/47/d78469b2bf68b341d090e45ababc5d7487bfe5": "132d0049cddcfd99924df2cce112e63c",
".git/objects/49/50abb9ce7f896fad83fee3da28cb3fbd106297": "491b9b70f7ee05128b0522f2ae538dee",
".git/objects/51/03e757c71f2abfd2269054a790f775ec61ffa4": "d437b77e41df8fcc0c0e99f143adc093",
".git/objects/55/d86548c8c288bec4f7e200c045c9982c237a38": "6e2c1f3f96402fe1c22fb2e13f43df22",
".git/objects/5d/eacc66bd704a543848197e0cbad792e65512c8": "985653b6c5c6aa50316ad9fafde580f9",
".git/objects/66/53bdb4dd8fa5bfc02ab91b3293f1e3e4c15f5f": "af22f28be680d2561e6bd1f4d98fa883",
".git/objects/68/43fddc6aef172d5576ecce56160b1c73bc0f85": "2a91c358adf65703ab820ee54e7aff37",
".git/objects/69/dd618354fa4dade8a26e0fd18f5e87dd079236": "8cc17911af57a5f6dc0b9ee255bb1a93",
".git/objects/6a/ff1f91b3cdee2b5ade0e5791846aaaaa5addd6": "d4a7b53d892b34e7606e30299545efb1",
".git/objects/6b/9862a1351012dc0f337c9ee5067ed3dbfbb439": "85896cd5fba127825eb58df13dfac82b",
".git/objects/6c/6fdb6b824422d787347637642bb8e525d9aff7": "897fdeb8f1a83895659a7ecfe4ad001b",
".git/objects/6f/7661bc79baa113f478e9a717e0c4959a3f3d27": "985be3a6935e9d31febd5205a9e04c4e",
".git/objects/71/d27d5916987b7ad4c11929ecafb8be66fac3c8": "736fa373682f477d50670cfd0def59ce",
".git/objects/73/1e34acfd1dca29d44da40c7bc700b6e533c8de": "dc4db7f9884c1a2cc630bcb9ebad2d13",
".git/objects/75/2916cf4ddee5aeae50979f65c984d0f71289e8": "7a6c3cb990e0007377d5ad13123d400c",
".git/objects/78/b404cc8534b3dae4389625dd55fdff1bb6a3b1": "424edca318ba521ef23c20547bd632ad",
".git/objects/79/7153dbf21da1d71b36c386a5a4cda3a03f4ef6": "5a360791e4ff294e358ff27d1da857af",
".git/objects/7b/63397bde46a512d608a2ab0fc1adf7c20442f3": "ec8cb32cd4efc2fd61ee2f18b8d0960f",
".git/objects/7c/3463b788d022128d17b29072564326f1fd8819": "37fee507a59e935fc85169a822943ba2",
".git/objects/7d/673bda1e2a757d0fb4db84dda4dcaaae10e716": "5a16e6d3b9d05249c0dc5bb693aaf55e",
".git/objects/81/d73c5c83f4aff9c7542c14729c058794927d0c": "3eb4cfbaf61a17430c69dc95d8169c25",
".git/objects/85/63aed2175379d2e75ec05ec0373a302730b6ad": "997f96db42b2dde7c208b10d023a5a8e",
".git/objects/85/7d9c8fecb7ef3079241d18c87b33c692655511": "495381abc1a90aa5ec87ba04e6d11227",
".git/objects/87/3e67b4120a700325d80b685496a9d6b69b8051": "d1f79cb7130a6b8d71da498fecd4a20a",
".git/objects/88/cfd48dff1169879ba46840804b412fe02fefd6": "e42aaae6a4cbfbc9f6326f1fa9e3380c",
".git/objects/8a/aa46ac1ae21512746f852a42ba87e4165dfdd1": "1d8820d345e38b30de033aa4b5a23e7b",
".git/objects/8b/64f58121400de0647394da0602e26ea4a8539f": "76a9dd1ab9ad1839e88b772277bca836",
".git/objects/8c/2332afec7e06fcf6ea1c6dc1bfe3ded90bf2fd": "98c8066d8c7bc17718c557250b3a5f77",
".git/objects/8e/21753cdb204192a414b235db41da6a8446c8b4": "1e467e19cabb5d3d38b8fe200c37479e",
".git/objects/8f/e7af5a3e840b75b70e59c3ffda1b58e84a5a1c": "e3695ae5742d7e56a9c696f82745288d",
".git/objects/90/7875bc12ae3d7562ce8295ad93caddbe9c643a": "f5c9ff9dfba1a7dc1c834c8ca455c97f",
".git/objects/91/c6ffd6b796179cdede15bd67a0af31552f3f0d": "94315452c42adea25ae0b6581891bfcf",
".git/objects/93/b363f37b4951e6c5b9e1932ed169c9928b1e90": "c8d74fb3083c0dc39be8cff78a1d4dd5",
".git/objects/94/e42a64de9eb6c6060dd27354cf8c7e036ac15b": "25a0d17ed72d4034aabdb5bd5eff5337",
".git/objects/96/6437cd02e16c063b5d35713d3f1ceb4b672f9c": "1663800c8d39fa2aa0d6140553a7d453",
".git/objects/9b/af0bc211a8f09bce29ffd9e92a51134d86029c": "e1aabf6192d4d9aa8d2242939365310c",
".git/objects/9c/1507ec945f8bbc67d789fdc8c16d0237ba24ae": "dc03bafbe525c5b2938020714cf06b2c",
".git/objects/9c/dccfd32517e1cd68760715c7d986708a2acb28": "d509b24243e9d3422f58a34099c83874",
".git/objects/a0/d5197c3ec8052126e92135682d8e188edcee9e": "3db6804350822609343ef66dc10d3b74",
".git/objects/a0/d9777c2f492f0efa214f61120a903190364549": "8fc28a3187edd1b38f031fe213b91466",
".git/objects/a0/dc521c6620e4a83201e7d5afc016bb05ff8695": "862d164be8f364e4b7162cfc43cd2831",
".git/objects/a3/0e28ac5ef7907d16023be301b669e2692d567b": "2fee55490fced8548d99bf53a3c2049d",
".git/objects/a5/f90df027daac943e37ecc36b9949e41799f919": "c89b400d9d08e1ba3b7591cad795e9b8",
".git/objects/a7/3f4b23dde68ce5a05ce4c658ccd690c7f707ec": "ee275830276a88bac752feff80ed6470",
".git/objects/a9/898e05729d1968e0579a9cf42ff57cc4fa258e": "d9eb1532938150eafd00378f8794e1ce",
".git/objects/ad/ced61befd6b9d30829511317b07b72e66918a1": "37e7fcca73f0b6930673b256fac467ae",
".git/objects/b2/a3aff4438e1e4e21ccc757c5c0764ffd90e096": "35fc6f0b4095093ccc89273df5167b3f",
".git/objects/b7/49bfef07473333cf1dd31e9eed89862a5d52aa": "36b4020dca303986cad10924774fb5dc",
".git/objects/b9/2a0d854da9a8f73216c4a0ef07a0f0a44e4373": "f62d1eb7f51165e2a6d2ef1921f976f3",
".git/objects/b9/3e39bd49dfaf9e225bb598cd9644f833badd9a": "666b0d595ebbcc37f0c7b61220c18864",
".git/objects/bb/26f01f2d5a9809686067a932d4c3dbc2ee0ea4": "7fad61c003f8167c3395374eb8c872c9",
".git/objects/bc/44dcd06e572d07b3cef9842bc48e6ed26edbd6": "7747b71e7635465cc9fdf78e7dd37a5a",
".git/objects/bd/194c7b144b258d65bf6cb00dcb407da49b8457": "6694d49eb541cc463b1fded8516e0a2d",
".git/objects/c1/fef6c1d4fbc75ac1d7e15bfac49e031e709c5e": "9aa93375c39159c295f30b5a995f5045",
".git/objects/c2/a0de4d96485d7fd29c384b2ae4f625baa0123d": "5e50f84cad8fcee1464364ce27e82a6f",
".git/objects/c2/ac212efe7904a5ad3987c175e990bec8959cc1": "e9172ad1b52b7d1cb5fb0935312edfb3",
".git/objects/c4/ef419c5e612027b6eabb61b6321b25d23b2139": "632a8bfa0faa6e14e84149e3933e1eac",
".git/objects/c7/41d43d0726cd2afc1eb58c3103f57a0b4431c9": "71a6281ee70be0ae1e6d8aef0239f143",
".git/objects/c8/3af99da428c63c1f82efdcd11c8d5297bddb04": "144ef6d9a8ff9a753d6e3b9573d5242f",
".git/objects/d3/1ac720c1e8d2351682cb8a85b63deded3b2c12": "8b338bdeca52151451d84094fabe580b",
".git/objects/d4/3532a2348cc9c26053ddb5802f0e5d4b8abc05": "3dad9b209346b1723bb2cc68e7e42a44",
".git/objects/d6/9c56691fbdb0b7efa65097c7cc1edac12a6d3e": "868ce37a3a78b0606713733248a2f579",
".git/objects/d6/ba4ca437b4ee8f1884bca3eabc0a7a1f07231d": "6fea11df2ee4007f38b1274b2ad6b48a",
".git/objects/d6/ca4841eab4d9caeaac9e890a88d49e039cae79": "0aa30df6f52cd05391eb9f9bad53f438",
".git/objects/d7/7cfefdbe249b8bf90ce8244ed8fc1732fe8f73": "9c0876641083076714600718b0dab097",
".git/objects/d9/0b3e5f32ea85c7da8d692834366679b69dd327": "a3683914989afba60251c759980157b0",
".git/objects/d9/5b1d3499b3b3d3989fa2a461151ba2abd92a07": "a072a09ac2efe43c8d49b7356317e52e",
".git/objects/d9/fcb17fe6bad5cbe0e28e912ab10e3fcf93c41b": "841650cca87d4209f882740f45e369c6",
".git/objects/dc/ac9e1e9372141ae09d27157cba3f74d6064995": "6f911ef16074d8d19f9a9be6d82d11c1",
".git/objects/de/3988f313b84b6bf090fa47be170a1aa0a5e222": "8159bc3002b6692f90f5f42b7c33128d",
".git/objects/e3/b504d47638a62439b1a1fa70b1ef899562139f": "d9134e5e4a10c27cb63f71a3c3bd0bb6",
".git/objects/e6/bf667b7df1000aa78ed7ab8eef30cd9e6c48b9": "096d0ecb0057de3a03d4a56076a7688c",
".git/objects/e9/94225c71c957162e2dcc06abe8295e482f93a2": "2eed33506ed70a5848a0b06f5b754f2c",
".git/objects/eb/9b4d76e525556d5d89141648c724331630325d": "37c0954235cbe27c4d93e74fe9a578ef",
".git/objects/f1/fe31cc047d6086fe586ca81af10ba09aca86ef": "b558e02b9aefc6d26098c36a0e8da864",
".git/objects/f3/3e0726c3581f96c51f862cf61120af36599a32": "afcaefd94c5f13d3da610e0defa27e50",
".git/objects/f5/72b90ef57ee79b82dd846c6871359a7cb10404": "e68f5265f0bb82d792ff536dcb99d803",
".git/objects/f6/e6c75d6f1151eeb165a90f04b4d99effa41e83": "95ea83d65d44e4c524c6d51286406ac8",
".git/objects/fa/42b8b2459290f306cf190c5887ac742457e607": "59c96b770187ace2628213273ff61928",
".git/objects/fb/f94d0a7be3362aa54cddf916e8142f8c78233e": "95453cae6f732af6b4b9c6d1748a3be1",
".git/objects/fd/05cfbc927a4fedcbe4d6d4b62e2c1ed8918f26": "5675c69555d005a1a244cc8ba90a402c",
".git/objects/fe/471fc05fb17a9f70c2954073f7cc49b8458e1c": "1cdb6481976f4fab08bfe789e641db34",
".git/refs/heads/main": "56e22a934191498d3e4810cbe8ba1c46",
".git/refs/remotes/origin/main": "56e22a934191498d3e4810cbe8ba1c46",
"assets/AssetManifest.bin": "693635b5258fe5f1cda720cf224f158c",
"assets/AssetManifest.bin.json": "69a99f98c8b1fb8111c5fb961769fcd8",
"assets/FontManifest.json": "dc3d03800ccca4601324923c0b1d6d57",
"assets/fonts/MaterialIcons-Regular.otf": "8b461d28263735da0fcd004ef04c0544",
"assets/NOTICES": "96dfc3ad33c24f350f67169dae2b9e13",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "33b7d9392238c04c131b6ce224e13711",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"assets/shaders/stretch_effect.frag": "40d68efbbf360632f614c731219e95f0",
"canvaskit/canvaskit.js": "8331fe38e66b3a898c4f37648aaf7ee2",
"canvaskit/canvaskit.js.symbols": "a3c9f77715b642d0437d9c275caba91e",
"canvaskit/canvaskit.wasm": "9b6a7830bf26959b200594729d73538e",
"canvaskit/chromium/canvaskit.js": "a80c765aaa8af8645c9fb1aae53f9abf",
"canvaskit/chromium/canvaskit.js.symbols": "e2d09f0e434bc118bf67dae526737d07",
"canvaskit/chromium/canvaskit.wasm": "a726e3f75a84fcdf495a15817c63a35d",
"canvaskit/skwasm.js": "8060d46e9a4901ca9991edd3a26be4f0",
"canvaskit/skwasm.js.symbols": "3a4aadf4e8141f284bd524976b1d6bdc",
"canvaskit/skwasm.wasm": "7e5f3afdd3b0747a1fd4517cea239898",
"canvaskit/skwasm_heavy.js": "740d43a6b8240ef9e23eed8c48840da4",
"canvaskit/skwasm_heavy.js.symbols": "0755b4fb399918388d71b59ad390b055",
"canvaskit/skwasm_heavy.wasm": "b0be7910760d205ea4e011458df6ee01",
"favicon.png": "5dcef449791fa27946b3d35ad8803796",
"flutter.js": "24bc71911b75b5f8135c949e27a2984e",
"flutter_bootstrap.js": "c4d5a6bb07096a4a39b61b93bd26de50",
"icons/Icon-192.png": "ac9a721a12bbc803b44f645561ecb1e1",
"icons/Icon-512.png": "96e752610906ba2a93c65f8abe1645f1",
"icons/Icon-maskable-192.png": "c457ef57daa1d16f64b27b786ec2ea3c",
"icons/Icon-maskable-512.png": "301a7604d45b3e739efc881eb04896ea",
"index.html": "8319f778103cb73f4b19bfd96aa212be",
"/": "8319f778103cb73f4b19bfd96aa212be",
"main.dart.js": "9cd2520dd25073e87142a6a5750a0bfe",
"manifest.json": "e5f5ecf00f3498e7b5ed10be7ed2f8be",
"version.json": "5bdb305c7def9be300fec84c81957b1c"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
