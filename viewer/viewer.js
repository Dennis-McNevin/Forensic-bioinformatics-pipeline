Str=new Meteor.Collection('str'); // Create a new MongoDB collection named Str
Samples=new Meteor.Collection('samples');  // Create a new MongoDB collection named Samples
Threshold=new Meteor.Collection('threshold'); // Create a new MongoDB collection named Threshold
Notes=new Meteor.Collection('notes'); // Create a new MongoDB collection named Notes
CurrentView=new Meteor.Collection('currentview'); // Create a new MongoDB collection named CurrentView
var sampleName;
var sampleFile;
var sample;
var samples;
var snps;
var layout='GlobalFiler';
var Schemas={}; 

// Create some code to run on the server if there is no data yet only when the application starts up
Meteor.startup(function () {
   fs = Npm.require('fs');
});

// Using a simple-schema package to attach a schema to the "CurrentView" collection
Schemas.CurrentView=new SimpleSchema({
        // To provide a single custom input type using comerc:autofrom-selectize
        // comerc:autofrom-selectize is an add-on package for aldeed:autoform 
	sample: {
		type: String,
		max:300,
		autoform: {
			type: "selectize", 
			firstOption: false,
			options: function() {
					// Pull some str out to the collection by Str.find({})
					// Sort str by _id, with the lowest id numbers appear first
					// Access an id on somethings from a Monogo collection by _id
				return _.uniq(Str.find({},{sort:{_id:1}}).fetch(),true,function(d) {return d.file}).map(function (c) { return {label:c.file,value:c.file+';'+c.orig}});
			}
		}
	},
	layout: {
		type: String,
		max: 50,
		autoform: {
			type: "selectize",
			firstOption: false,
			options: function() {
				return _.map(["GlobalFiler","PowerPlex Fusion","PowerPlex 21","Promega CS7","Qiagen HDplex","Qiagen Argus X12","Y-Filer Plus","Y-Filer 17","PowerPlex Y-23"],function(c) {return {label:c,value:c};});
			}
		}
	}
});

// Once the simpleSchema is defined, attach it to the collection
CurrentView.attachSchema(Schemas.CurrentView); 

// Attach a schema to the "Notes" collection
Schemas.Notes=new SimpleSchema({notes: {type: String,autoform:{rows:2}}});
Notes.attachSchema(Schemas.Notes);

// An object contains loci and corresponding chromosome coordinates
var coord={'D1S1656': 'chr1:230905363-230905429',
	'TH01': 'chr11:2192319-2192345',
	'VWA': 'chr12:6903103-6093254',
	'D12S391': 'chr12:12449948-12450000',
	'D13S317': 'chr13:82722161-82722203',
	'PentaE': 'chr15:97374246-97374269',
	'D16S539': 'chr16:86386309-86386351',
	'D18S51': 'chr18:60948901-60948971',
	'D19S433': 'chr19:30417141-30417192',
	'D21S11': 'chr21:20554292-20554417',
	'PentaD': 'chr21:45056087-45056150',
	'TPOX': 'chr2:1493426-1493456',
	'D2S441': 'chr2:68239080-68239128',
	'D2S1338': 'chr2:218879577-218879647',
	'D3S1358': 'chr3:45582232-45582294',
	'FGA': 'chr4:155508889-155508975',
	'D5S818': 'chr5:123111251-123111293',
	'CSF1PO': 'chr5:149455888-149455938',
	'SE33': 'chr6:88986849-88987076',
	'D7S820': 'chr7:83789543-83789593',
	'D8S1179': 'chr8:125907116-125907158',
	'HPRTB': 'chrX:133615404-133615691',
	'DYS391': 'chrY:14102796-14102838',
	'DYS635': 'chrY:14379565-14379655',
	'DYS434': 'chrY:14466534-14466568',
	'DYS437': 'chrY:14466995-14467057',
	'DYS435': 'chrY:14496299-14496333',
	'DYS439': 'chrY:14515313-14515363',
	'DYS389B.2': 'chrY:14612243-14612310',
	'DYS389I': 'chrY:14612244-14612289',
	'DYS389B.1': 'chrY:14612359-14612405',
	'DYS388': 'chrY:14747536-14747570',
	'DYS442': 'chrY:14761104-14761168',
	'DYS438': 'chrY:14937825-14937873',
	'DYS441': 'chrY:14981832-14981908',
	'DYS495': 'chrY:15011301-15011346',
	'DYS436': 'chrY:15203863-15203897',
	'DYS447': 'chrY:15278741-15278854',
	'DYS413a/b': 'chrY:16099089-16099133',
	'DYS641': 'chrY:16134297-16134335',
	'DYS472': 'chrY:16508485-16508507',
	'DYS565': 'chrY:16526733-16526775',
	'DYS390': 'chrY:17274948-17275042',
	'DYS511': 'chrY:17304924-17304958',
	'DYS717': 'chrY:17313246-17313324',
	'DYS492': 'chrY:17414338-17414369',
	'DYS643': 'chrY:17426013-17426066',
	'DYS638': 'chrY:17645492-17645534',
	'DYS534': 'chrY:18392977-18393035',
	'DYS533': 'chrY:18393227-18393273',
	'DYS607': 'chrY:18414383-18414457',
	'GATA-A10': 'chrY:18718880-18718938',
	'GATA-H4': 'chrY:18743554-18743600',
	'DYS617': 'chrY:19081519-19081553',
	'DYS426': 'chrY:19134851-19134885',
	'DYS444': 'chrY:19226193-19226247',
	'DYS537': 'chrY:19358851-19358889',
	'YCAIIa/b': 'chrY:19622112-19622156',
	'DYS425': 'chrY:20203509-20203537',
	'DYS395S1a/b': 'chrY:20440394-20440433',
	'DYS385a/b': 'chrY:20842519-20842573',
	'DYS461': 'chrY:21050691-21050737',
	'DYS460': 'chrY:21050843-21050881',
	'DYS462': 'chrY:21317048-21317090',
	'DYS494': 'chrY:21386169-21386197',
	'DYS549': 'chrY:21520225-21520275',
	'DYS452': 'chrY:21620479-21620632',
	'DYS594': 'chrY:21656838-21656886',
	'DYS445': 'chrY:22092603-22092649',
	'DYS485': 'chrY:22099635-22099681',
	'DYS714': 'chrY:22147732-22147865',
	'DYS578': 'chrY:22562565-22562599',
	'DYS556': 'chrY:22601454-22601496',
	'DYS392': 'chrY:22633874-22633911',
	'DYS636': 'chrY:22634858-22634900',
	'DYS557': 'chrY:23234713-23234775',
	'DYS406S1': 'chrY:23843596-23843634',
	'DYS448.1': 'chrY:24365071-24365136',
	'DYS448.2': 'chrY:24365179-24365225',
	'DYS589': 'chrY:24485694-24485757',
	'DYS459a/b': 'chrY:26078852-26078890',
	'DYS464a/b/c/d': 'chrY:27087612-27087670',
	'DYS393': 'chrY:3131153-3131199',
	'DYS446': 'chrY:3131459-3131527',
	'DYS640': 'chrY:3279703-3279737',
	'DYS490': 'chrY:3443766-3443800',
	'DYS505': 'chrY:3640832-3640878',
	'DYS572': 'chrY:3679661-3679699',
	'DYS456': 'chrY:4270961-4271019',
	'DYS570': 'chrY:6861232-6861298',
	'DYS455': 'chrY:6911570-6911612',
	'DYS576': 'chrY:7053360-7053426',
	'DYS522': 'chrY:7415626-7415664',
	'DYS575': 'chrY:7436258-7436296',
	'DYS463': 'chrY:7643510-7643628',
	'DYS520': 'chrY:7730433-7730511',
	'DYS458': 'chrY:7867881-7867943',
	'DYS450': 'chrY:8126301-8126344',
	'DYS449.1': 'chrY:8218015-8218074',
	'DYS449.2': 'chrY:8218125-8218179',
	'DYS454': 'chrY:8224157-8224199',
	'DYS481': 'chrY:8426379-8426443',
	'DYS531': 'chrY:8466196-8466238',
	'DYS590': 'chrY:8555981-8556019',
	'DYS568': 'chrY:8822556-8822594',
	'DYS487': 'chrY:8914175-8914212',
	'DYS19/DYS394': 'chrY:9521990-9522052'};

// 4. Generate another var to format SNP data for IGV
// 4. Add all aiSNPs from bed file
var coordSNP={'rs798443': 'chr2:7968224-7968324',
		'rs11652805': 'chr17:62987100-62987200',
		'rs10497191': 'chr2:158667166-158667266',
		'rs16891982': 'chr5:33951642-33951742',
		'rs12439433': 'chr15:36219984-36220084',
		'rs2986742': 'chr1:6550325-6550425',
		'rs6541030': 'chr1:12608127-12608227',
		'rs647325': 'chr1:18170835-18170935',
		'rs4908343': 'chr1:27931647-27931747',	
		'rs1325502': 'chr1:42360219-42360319',
		'rs12130799': 'chr1:55663321-55663421',	
		'rs3118378': 'chr1:68849636-68849736',
		'rs3737576': 'chr1:101709512-101709612',	
		'rs7554936': 'chr1:151122438-151122538',
		'rs2814778': 'chr1:159174632-159174732',	
		'rs1040404': 'chr1:168159839-168159939',
		'rs1407434': 'chr1:186148981-186149081',	
		'rs4951629': 'chr1:212786832-212786932',
		'rs316873': 'chr1:242342453-242342553',	
		'rs798443': 'chr2:7968224-7968324', //
		'rs7421394': 'chr2:14756298-14756398',
		'rs1876482': 'chr2:17362517-17362617',
		'rs1834619': 'chr2:17901434-17901534',
		'rs4666200': 'chr2:29538360-29538460',
		'rs4670767': 'chr2:37941345-37941445',
		'rs13400937': 'chr2:79864872-79864972',
		'rs3827760': 'chr2:109513550-109513650', //
		'rs260690': 'chr2:109579687-109579787',
		'rs6754311': 'chr2:136707931-136708031',
		'rs10496971': 'chr2:145769892-145769992',
		'rs10497191': 'chr2:158667116-158667216', //
		'rs2627037': 'chr2:179606487-179606587',
		'rs1569175': 'chr2:201021903-201022003',
 		'rs4955316': 'chr3:30415561-30415661',
 		'rs9809104': 'chr3:39146378-39146478',
 		'rs6548616': 'chr3:79399524-79399624',
 		'rs12629908': 'chr3:120522665-120522765',
 		'rs12498138': 'chr3:121459538-121459638',
 		'rs9845457': 'chr3:135914425-135914525',
 		'rs734873': 'chr3:147750304-147750404',
 		'rs2030763': 'chr3:179964676-179964776',
 		'rs1513181': 'chr3:188574945-188575045',
 		'rs9291090': 'chr4:5390586-5390686',
 		'rs4833103': 'chr4:38815451-38815551',
 		'rs10007810': 'chr4:41554313-41554413',
 		'rs1369093': 'chr4:73245140-73245240',
 		'rs385194': 'chr4:85309027-85309127',
 		'rs1229984': 'chr4:100239268-100239368',
 		'rs3811801': 'chr4:100244268-100244368',
 		'rs7657799': 'chr4:105375372-105375472',
 		'rs2702414': 'chr4:179399472-179399572',
 		'rs316598': 'chr5:2364575-2364675',
 		'rs870347': 'chr5:6844984-6845084',
 		'rs16891982': 'chr5:33951642-33951742',
 		'rs37369': 'chr5:35037064-35037164',
 		'rs6451722': 'chr5:43711327-43711427',
 		'rs12657828': 'chr5:79085675-79085775',
 		'rs6556352': 'chr5:155471663-155471763',
 		'rs1500127': 'chr5:165739931-165740031',
 		'rs7722456': 'chr5:170202933-170203033',
 		'rs6422347': 'chr5:177863032-177863132',
 		'rs1040045': 'chr6:4747108-4747208',
		'rs2504853': 'chr6:12535060-12535160',
		'rs7745461': 'chr6:21911565-21911665',
		'rs192655': 'chr6:90518227-90518327', //
		'rs3823159': 'chr6:136482676-136482776',
		'rs4463276': 'chr6:145055280-145055380',
		'rs4458655': 'chr6:163221741-163221841',
		'rs1871428': 'chr6:168665709-168665809',
		'rs731257': 'chr7:12669200-12669300',
		'rs917115': 'chr7:28172535-28172635',
		'rs32314': 'chr7:32179073-32179173',
		'rs2330442': 'chr7:42380020-42380120',
		'rs4717865': 'chr7:73454148-73454248',
		'rs10954737': 'chr7:83532996-83533096',
		'rs705308': 'chr7:97695312-97695412',
		'rs7803075': 'chr7:130742015-130742115',
		'rs10236187': 'chr7:139447326-139447426',
		'rs6464211': 'chr7:151873802-151873902',
 		'rs10108270': 'chr8:4190742-4190842',
 		'rs3943253': 'chr8:13359449-13359549',
 		'rs1471939': 'chr8:28941254-28941354',
 		'rs1462906': 'chr8:31896541-31896641',
 		'rs12544346': 'chr8:86424565-86424665',
 		'rs6990312': 'chr8:110602266-110602366',
 		'rs2196051': 'chr8:122124251-122124351',
 		'rs7844723': 'chr8:122908452-122908552',
 		'rs2001907': 'chr8:140241130-140241230',
 		'rs1871534': 'chr8:145639630-145639730',
 		'rs10511828': 'chr9:28628449-28628549',
 		'rs3793451': 'chr9:71659229-71659329',
 		'rs2306040': 'chr9:93641148-93641248',
 		'rs10513300': 'chr9:120130155-120130255',
 		'rs3814134': 'chr9:127267638-127267738',
 		'rs2073821': 'chr9:135933071-135933171',
 		'rs3793791': 'chr10:50841653-50841753',
 		'rs4746136': 'chr10:75300943-75301043',
 		'rs4918664': 'chr10:94921014-94921114',
 		'rs4918842': 'chr10:115316761-115316861',
 		'rs4880436': 'chr10:134650052-134650152',
 		'rs10839880': 'chr11:7850265-7850365',
 		'rs1837606': 'chr11:15838086-15838186',
 		'rs2946788': 'chr11:24010479-24010579',
 		'rs174570': 'chr11:61597161-61597261',
 		'rs11227699': 'chr11:66898441-66898541',
 		'rs1079597': 'chr11:113296235-113296335',
 		'rs948028': 'chr11:120644396-120644496',
 		'rs2416791': 'chr12:11701437-11701537',
 		'rs1513056': 'chr12:17407741-17407841',
 		'rs214678': 'chr12:47676899-47676999',
 		'rs772262': 'chr12:56163683-56163783',
 		'rs2070586': 'chr12:109277669-109277769',
 		'rs2238151': 'chr12:112211782-112211882',
 		'rs671': 'chr12:112241715-112241815',
 		'rs1503767': 'chr12:118889437-118889537',
 		'rs9319336': 'chr13:27624305-27624405',
 		'rs7997709': 'chr13:34847686-34847786',
 		'rs1572018': 'chr13:41715231-41715331',
 		'rs2166624': 'chr13:42579934-42580034',
 		'rs7326934': 'chr13:49070461-49070561',
 		'rs9530435': 'chr13:75993836-75993936',
 		'rs9522149': 'chr13:111827116-111827216',
 		'rs1760921': 'chr14:20818080-20818180',
 		'rs2357442': 'chr14:52607916-52608016',
 		'rs1950993': 'chr14:58238636-58238736',
 		'rs8021730': 'chr14:67886730-67886830',
 		'rs946918': 'chr14:83472817-83472917',
 		'rs200354': 'chr14:99375270-99375370',
 		'rs3784230': 'chr14:105679004-105679104',
 		'rs1800414': 'chr15:28196986-28197086',
 		'rs12913832': 'chr15:28365567-28365667',
 		'rs12439433': 'chr15:36219984-36220084',
 		'rs735480': 'chr15:45152320-45152420',
 		'rs1426654': 'chr15:48426433-48426533',
 		'rs2899826': 'chr15:74734449-74734549',
 		'rs8035124': 'chr15:92105657-92105757',
 		'rs4984913': 'chr16:740415-740515',
 		'rs4781011': 'chr16:10975260-10975360',
 		'rs818386': 'chr16:65406657-65406757',
 		'rs2966849': 'chr16:85183631-85183731',
 		'rs459920': 'chr16:89730776-89730876',
 		'rs1879488': 'chr17:1401562-1401662',
 		'rs4411548': 'chr17:40658482-40658582',
 		'rs2593595': 'chr17:41056194-41056294',
 		'rs17642714': 'chr17:48726081-48726181',
 		'rs4471745': 'chr17:53568833-53568933',
 		'rs2033111': 'chr17:53788229-53788329',
 		'rs11652805': 'chr17:62987100-62987200', //
 		'rs10512572': 'chr17:69512048-69512148',
 		'rs2125345': 'chr17:73782140-73782240',
 		'rs4798812': 'chr18:9420453-9420553',
 		'rs2042762': 'chr18:35277571-35277671',
 		'rs7226659': 'chr18:40488228-40488328',
 		'rs7238445': 'chr18:49781493-49781593',
 		'rs881728': 'chr18:59333057-59333157',
 		'rs3916235': 'chr18:67578880-67578980',
 		'rs4891825': 'chr18:67867612-67867712',
 		'rs874299': 'chr18:75056233-75056333',
 		'rs7251928': 'chr19:4077045-4077145',
 		'rs8113143': 'chr19:33652196-33652296',
 		'rs3745099': 'chr19:52901854-52901954',
 		'rs2532060': 'chr19:55614872-55614972',
 		'rs6104567': 'chr20:10195382-10195482',
 		'rs3907047': 'chr20:54000863-54000963',
 		'rs310644': 'chr20:62159453-62159553',
 		'rs2835370': 'chr21:37885574-37885674',
 		'rs1296819': 'chr22:18076495-18076595',
 		'rs4821004': 'chr22:32366308-32366408',
 		'rs2024566': 'chr22:41697287-41697387',
 		'rs5768007': 'chr22:48207821-48207921', //end of aiSNP
 		'rs1490413': 'chr1:4367272-4367372', // start of iiSNP
 		'rs7520386': 'chr1:14155351-14155451',
 		'rs4847034': 'chr1:105717580-105717680',
 		'rs560681': 'chr1:160786619-160786719',
 		'rs10495407': 'chr1:238439257-238439357',
 		'rs891700': 'chr1:239881875-239881975',
 		'rs1413212': 'chr1:242806746-242806846',
 		'rs876724': 'chr2:114923-115023',
 		'rs1109037': 'chr2:10085671-10085771',
 		'rs993934': 'chr2:124109162-124109262',
 		'rs12997453': 'chr2:182413208-182413308',
 		'rs907100': 'chr2:239563528-239563628',
 		'rs1357617': 'chr3:961731-961831',
 		'rs4364205': 'chr3:32417593-32417693',
 		'rs1872575': 'chr3:113804928-113805028',
 		'rs1355366': 'chr3:190806057-190806157',
 		'rs6444724': 'chr3:193207329-193207429',
 		'rs2046361': 'chr4:10969008-10969108',
 		'rs6811238': 'chr4:169663564-169663664',
 		'rs1979255': 'chr4:190318029-190318129',
 		'rs717302': 'chr5:2879344-2879444	',
 		'rs159606': 'chr5:17374847-17374947',
 		'rs7704770': 'chr5:159487902-159488002',
 		'rs251934': 'chr5:174778627-174778727',
 		'rs338882': 'chr5:178690674-178690774',
 		'rs13218440': 'chr6:12059903-12060003',
 		'rs214955': 'chr6:152697655-152697755',
 		'rs727811': 'chr6:165045283-165045383',
 		'rs6955448': 'chr7:4310314-4310414',
 		'rs917118': 'chr7:4456952-4457052',
 		'rs321198': 'chr7:137029787-137029887',
 		'rs737681': 'chr7:155990762-155990862',
 		'rs10092491': 'chr8:28411021-28411121',
 		'rs4288409': 'chr8:136839178-136839278',
 		'rs2056277': 'chr8:139399065-139399165',
 		'rs1015250': 'chr9:1823723-1823823',
 		'rs7041158': 'chr9:27985887-27985987',
 		'rs1463729': 'chr9:126881397-126881497',
 		'rs1360288': 'chr9:128968012-128968112',
 		'rs10776839': 'chr9:137417257-137417357',
 		'rs826472': 'chr10:2406580-2406680',
 		'rs735155': 'chr10:3374127-3374227',
 		'rs3780962': 'chr10:171932295-17193395',
 		'rs740598': 'chr10:118506848-118506948',
 		'rs964681': 'chr10:132698368-132698468',
 		'rs1498553': 'chr11:5708977-5709077',
 		'rs901398': 'chr11:11096170-11096270',
 		'rs10488710': 'chr11:115207125-115207225',
 		'rs2076848': 'chr11:134667495-134667595',
 		'rs2269355': 'chr12:6945863-6945963',
 		'rs2111980': 'chr12:106328203-106328303',
 		'rs10773760': 'chr12:130761645-130761745',
 		'rs1335873': 'chr13:20901673-20901773',
 		'rs1886510': 'chr13:22374649-22374749',
 		'rs1058083': 'chr13:100038182-100038282',
 		'rs354439': 'chr13:106938360-106938460',
 		'rs1454361': 'chr1425850781-25850871',
 		'rs722290': 'chr14:53216672-53216772',
 		'rs873196': 'chr14:98845480-98845580',
 		'rs4530059': 'chr14:104769098-104769198',
 		'rs2016276': 'chr15:24571745-24571845',
 		'rs1821380': 'chr15:39313351-39313451',
 		'rs1528460': 'chr15:55210654-55210754',
 		'rs729172': 'chr16:5606146-5606246',
 		'rs2342747': 'chr16:5868649-5868749',
 		'rs430046': 'chr16:78017000-78017100',
 		'rs1382387': 'chr16:80106310-80106410',
 		'rs9905977': 'chr17:2919342-2919442',
 		'rs740910': 'chr17:5706572-5706672',
 		'rs938283': 'chr17:77468447-77468547',
 		'rs2292972': 'chr17:80765737-80765837',
 		'rs1493232': 'chr18:1127935-1128035',
 		'rs9951171': 'chr18:9749828-9749928',
 		'rs1736442': 'chr18:55225726-55225826',
 		'rs1024116': 'chr18:75432335-75432435',
 		'rs719366': 'chr19:28463286-28463386',
 		'rs576261': 'chr19:39559756-39559856',
 		'rs1031825': 'chr20:4447432-4447532',
 		'rs445251': 'chr20:15124882-15124982',
 		'rs1005533': 'chr20:39487059-39487159',
 		'rs1523537': 'chr20:51296111-51296211',
 		'rs722098': 'chr21:16685547-16685647',
 		'rs2830795': 'chr21:28608112-28608212',
 		'rs2831700': 'chr21:29679636-29679736',
 		'rs914165': 'chr21:42415878-42415978',
 		'rs221956': 'chr21:43606946-43607046',
 		'rs733164': 'chr22:27816733-27816833',
 		'rs987640': 'chr22:33559457-33559557',
 		'rs2040411': 'chr22:47836361-47836461',
 		'rs1028528': 'chr22:48362239-48362339',
 		'rs2534636': 'chrY:2657125-2657225',
 		'rs35284970': 'chrY:2734803-2734903',
 		'rs9786184': 'chrY:2887773-2887873',
 		'rs9786139': 'chrY:6753468-6753568',
 		'rs16981290': 'chrY:7568517-7568617',
 		'rs17250845': 'chrY:8418876-8418976',
 		'rs372687543': 'chrY:8467239-8467339',
 		'rs369616152': 'chrY:14000973-14001073',
 		'rs17306671': 'chrY:14031283-14031383',
 		'rs4141886': 'chrY:14197816-14197916',
 		'rs2032595': 'chrY:14813940-14814040',
 		'rs2032599': 'chrY:14851503-14851603',
 		'rs20320': 'chrY:14898112-14898212',
 		'rs2032602': 'chrY:14954229-14954329',
 		'rs8179021': 'chrY:15018531-15018631',
 		'rs2032624': 'chrY:15026373-15026473',
 		'rs2032636': 'chrY:15027478-15027578',
 		'rs9341278': 'chrY:15469673-15469773',
 		'rs2032658': 'chrY:15581932-15582032',
 		'rs2319818': 'chrY:16354657-16354757',
 		'rs17269816': 'chrY:17053720-17053820',
 		'rs17222573': 'chrY:17891190-17891290',
 		'rs372157627': 'chrY:20834616-20834716',
 		'rs3848982': 'chrY:21717157-21717257',
 		'rs3900': 'chrY:21730206-21730306',
 		'rs3911': 'chrY:21733403-21733503',
 		'rs2032631': 'chrY:21867736-21867836',
 		'rs2032673': 'chrY:21894007-21894107',
 		'rs2032652': 'chrY:21917262-21917362',
 		'rs16980426': 'chrY:22214170-22214270',
 		'rs13447443': 'chrY:22739250-22739350',
 		'rs17842518': 'chrY:23443920-23444020',
 		'rs2033003': 'chrY:23550873-23550973'}; // end of iiSNP(missing one SNP from bed file as wrong info


// 		'': 'chrY:',
// rs798443': 'chr2:7968274-7968275',
// 'rs11652805': 'chr17:62987150-62987151',
// 'rs10497191': 'chr2:158667216-158667217',
// 'rs16891982': 'chr5:33951692-33951693'
// 'rs12439433': 'chr15:36220034-36220035'

if (Meteor.isClient) {  // code here will be running on the web browser only

	Meteor.subscribe("str"); 
	// Subscribe to a record set, tell the server to send records to the client
	// The client stores these records in local Minimongo collections
	// with the same name of the server's publish() call


	Template.registerHelper("Schemas",Schemas); 
	// Add all SimpleSchema instances to a Schemas object and register that object as a helper


	AutoForm.setDefaultTemplate('materialize');
	// Add materialize templates for autoform

	Template.menu.events({
		'change #sampleSelect': function(e){
			console.log('Selected sample '+e.target.value);
			var values=e.target.value.split(';'); // Return a new string with ; being replaced by ,
			sampleName=values[0];
			sampleFile=values[1];
			builtLobstr();
		},
		'change #layoutSelect': function(e){
			console.log('Selected layout '+e.target.value);
			layout=e.target.value;
			builtLobstr();
		}
	});
	
	Session.setDefault('viz','home'); // Set viz in the session if viz is hasn't been set before
					  // home is the new value for viz
	
	Template.body.helpers({ // Template helpers send functions to the "body" templates
		currentViz: function(){
			return Session.get('viz');
		}
	})
	
	Template.snptable.onCreated(function(){
		Session.set('snps',[]);
	});
	
	Template.snptable.helpers({ // Template helpers send functions to the "snptable" templates.
		snps: function() {
			return Session.get('snps');
		}
	});
	
	Template.snptable.events({ // Add click events to the "snptable" template
		// 4. Allow linkage to IGV
		'click .linkage-to-igv':function(e){
			var region=coordSNP[this.rsid]; // 4. this.category replaces with this.rsid
			console.log("Clicked on "+p(this.rsid)+'. Opening '+region); // 4. this.rsid
			var vcf=sampleFile.replace(".txt","").replace(".codis","").replace(".ystr","").replace(".snp","")+".vcf";
			var bam=vcf.replace("_lobstr.vcf","_sorted.bam");
			Meteor.call("getResultsDir", function(err, res) {
				var resultsDir=res;
					console.log('resultsDir='+resultsDir);
					window.open('http://localhost:60151/load?genome=hg19&merge=false&locus='+region+'&file=file://'+resultsDir+'/'+vcf+',file://'+resultsDir+'/'+bam+',file://'+resultsDir+'/../lobSTR_hg19.gff3');
			});
		},
//		'mouseover [data-toggle="popover"]': function(e){
		'click': function(e){
			var p = $(e.currentTarget).popover({ // Popovers are not CSS-only plugins, and must therefore be initialized with jQuery:
				// Pulling off the specified element of the event called currentTarget
				// The current target of the event is the SNP that they clicked on
				html:true // Use HTML to render the labels
			});
			var cTarget = e.currentTarget;
			$(cTarget.id+'con').show();  // what is 'con'?

			var refC = parseInt(cTarget.getAttribute("refC")); 
			var altC = parseInt(cTarget.getAttribute("altC")); 
			// The name of the attribute (refC) in which we want to get the value from, and then parses the string value and returns an integer
			// eg. "2" returns 2
			new Highcharts.Chart({
				chart: {
					renderTo: cTarget.id+'con', 
					// The HTML element where the chart will be rendered. 
					type: 'column' // Draw the column chart
				},
				exporting:{enabled: true},
				tooltip: { formatter: function () { // tooltip shows extra info when user moves the mouse pointer over an element
					return '<b>' + this.x + '</b>: '+ this.y +' read'+((this.y==1)?'':'s') + '<br/><i>('+this.point.p+"%)</i>";
							// this.x is the allele
							// The <b> tag specifies bold text
									// this.y is the read for that allele
														// percentage in italic
				} },
		        plotOptions: {
			    series: {
				pointWidth: 50, // 3. Adjust the width for each column
			    animation: false // 3. Remove animation
			    },
		            column: {
		                dataLabels: { enabled: true, crop: false, overflow: 'none'} // 3. To display data labels outside the plot area, not align them inside the plot area
		            }
		        },
		        title:{text:null},
		        legend:{enabled:false},
		        credits:{enabled:false},
		        xAxis: {
		       		 categories: [cTarget.getAttribute("ref"),cTarget.getAttribute("alt")] // get the value (allele) from the attributes ref and alt
		        },
		        yAxis: {
				minorGridLineDashStyle: 'longdash', // 3. Make the dash of the minor grid lines
				minorTickInterval: 'auto', // 3. Set the minor tick interval as a fifth of the tickInterval (auto)
				minorTickWidth: 0, // 3. The pixel width pf the minor tick mark
		            title: {
		                text: 'reads',
		                useHTML: true,
		                style: { // Rotates an element clockwise
		                    "-webkit-transform": "rotate(90deg)", // Safari
		                    "-moz-transform": "rotate(90deg)", 
		                    "-o-transform": "rotate(90deg)"
		                }
		            }
		        },
			// A series is a set of datas. All data plotted on a chart comes from the series object.
		        series: [{ name:'reads', data: [{y: refC, p: (100*refC/(refC+altC)).toFixed(2)}, // Convert a number into a string, keeping only two decimals
							{y: altC, p: (100*altC/(refC+altC)).toFixed(2)}] 
				}]
		    });
		}
	});
	

	function builtLobstr(collection) {
	//	samples=Str.find({},{ sort:{_id:1}}).map(function (doc){return doc['sample']});
	//	samples=_.uniq(Str.find({},{sort:{_id:1}}).fetch(),true,function(d) {return d.file});
	//	console.log('samples: '+p(samples)); fields:{_id:1,type:1},
	//	console.log('sampleName: '+p(sampleName));
		sample=Str.findOne({_id:sampleName+'|'+layout}); // Pull str out of a MongoDB. Not pull out sort of a whole bunch of things but only one entry by using findOne
		sampleType=typeof sample; //typeof operator can return either string, number, boolean and undefined
	//	console.log('sample('+p(sampleType)+'): '+p(sample));
		if(sampleType!='undefined') { // If sampleType is NOT undefined, do the for loop
			for(x = 0; x < 8; x++) {  
				if(typeof sample.categoriesArray[x]=='undefined' || sample.categoriesArray[x].length<1) {
					$('#containerChart'+x).hide(); // hides the element with id="containerChart"
				}else {
					$('#containerChart'+x).show();
				}
				var graphSeries = eval("GraphSeries");
				graphSeries.data = [];
				graphSeries.name = "GraphSeries" + x;
				graphSeries.point.events.click = function() {
					Meteor.call('runCode', function (err, response) {
						console.log('cmd: '+response);
						alert ('Category: '+ this.category +'<br/>'+response);
					});
				}
				var graphOptions = eval("GraphOptions");
				graphOptions.series = sample.seriesArray[x];
				graphOptions.xAxis.categories = sample.categoriesArray[x];
				graphOptions.chart.renderTo = 'containerChart'+x;
	//			if(x==0) {
	//				graphOptions.title.text = sample.title;
	//			}else {
	//				graphOptions.title.text = null;
	//			}
				Session.set('viz','lobstr'); // now lobstr is the new value for viz, given that viz has been set before
				new Highcharts.Chart(graphOptions); // The graphOptions object is created below and added to the chart here by passing it to the chart constructor
			}
		}else {
			sample=Str.findOne({_id:sampleName}); // Pull one entry out of a MongoDB using findOne
			if(sample!=null) {
				Session.set('snps',sample.snpsArray);
				Session.set('viz','snptable');
	//			console.log(JSON.stringify(sample.snpsArray));
			}
		}
	}
	
	// Use a JavaScript object structure provided by Highcharts to define the optionsof a chart
	var GraphOptions = {
	    chart: { type: 'column', plotBorderColor: '#000000', plotBorderWidth: 1}, // 8. Delete renderTo. Add plotBorderColor and plotBorderWidth
		title:{ text:null },
		subtitle:{ text:null },
		credits: { enabled: false },
	    legend: { enabled: false },
	    exporting:{enabled: false},
		tooltip: { formatter: function () { // hovering event
			if(this.y>0) { // when no. of reads > 0, show hovering event
				AnalyticThresh="Analytic T: " + this.point.at+"%";
				StochasticThresh="Stochastic T: " + this.point.st+"%";
				StutterThresh="Stutter T: " + this.point.tt+"%";
					// If allele read coverage % is smaller than the threshold %, threshold% is shown in bold
					if(this.point.p < this.point.at) {
						AnalyticThresh='<font color="#0000ff"><b>'+AnalyticThresh+'</b></font>';
					}
					if(this.point.p < this.point.st) {
						StochasticThresh='<font color="#ff0000"><b>'+StochasticThresh+'</b></font>';
					}
					if(this.point.p < this.point.tt) {
						StutterThresh='<font color="#ff0000"><b>'+StutterThresh+'</b></font>';
					}
				return '<b>'+this.x+'</b> allele <b>'+this.series.name + '</b><br/>'+ 
					// this.x = locus
					// this.series.name = allele
					this.y+' read'+((this.y==1)?'':'s') +
					// this.y = no. of reads
					' <i>('+this.point.p+"%)</i><br/>Ref allele: " + 
						// this.point.p = percentage reads
					this.point.r+"<br/>"+AnalyticThresh+"<br/>"+StochasticThresh+"<br/>"+StutterThresh;
					// this.point.r = reference allele
			}
		} },
		plotOptions: {
			column: {
				dataLabels: {
					enabled: true,
					// Callback JS function to format the data label
					formatter: function(){ return this.point.l; }, // Define the point object as this.point.l
					style: { fontSize:'8pt', color:'#101010',  crop: false, overflow: 'none'}, // 7. To display data labels outside the plot area, not align them inside the plot area (not working at all)
					// The x and y position offset of the label relative to the point:
					x:0, // 7. Defaults to 0 (can be modified so that labels line up with the column)
					y:0, // 7. (working)
					align:'center', 
					allowOverlap: false // 7. Add allowOverlap: false to hide overlapping data labels
				},
			},
			series: { 
				
				// maxPointWidth: 20, // The maximum allowed pixel width for a column
				pointWidth: 5, // 7. Set a fixed width for each column 
				//pointPadding: 0.1, // 7. Padding betweeen each column in x axis units
				//groupPadding: 0.2, // 7. Padding between each value groups in x axis units
				point: {
					events: {
						click: function(e) {
							// Open IGV
							var region=coord[this.category];
							console.log("Clicked on "+p(this.category)+'. Opening '+region);
							var vcf=sampleFile.replace(".txt","").replace(".codis","").replace(".ystr","").replace(".snp","")+".vcf";
							var bam=vcf.replace("_lobstr.vcf","_sorted.bam");
							Meteor.call("getResultsDir", function(err, res) {
								var resultsDir=res;
								console.log('resultsDir='+resultsDir);
								window.open('http://localhost:60151/load?genome=hg19&merge=false&locus='+region+'&file=file://'+resultsDir+'/'+vcf+',file://'+resultsDir+'/'+bam+',file://'+resultsDir+'/../lobSTR_hg19.gff3');
							});
//							Session.set("viz","strchart"); #new method not plugged in yet
						}
					}
				}
			}
		},

// yAxis: [{ className: 'STRchartyAxisColour', title: {text: 'Read Counts'} }], // 8. Adding 'className' is not working
		yAxis: { // min:0, 
			minTickInterval: 50, // 8. Add a minTickInterval
			title:{text:'Read Counts', 
				style:{fontSize: '10pt', color:'black'} // 8. Set font size and color
			}, 
			gridLineDashStyle: 'longdash', // 8. Grid line is set to longdash
			lineColor: '#000000', // 8. Set y axis long colour
			lineWidth: 1, // 8. Set y axis line width
			labels: {
				overflow:'justify', //  If "justify", labels will not render outside the legend area.
				 style: { color: 'black', fontSize: '10pt'} //8. Make y axis label black in colour. Set font size to 12px
				}
		}, 
										
				
		xAxis: { categories: [],
			 lineColor: '#000000', // 8.
			 labels: { style: { color: 'black', fontSize: '12pt'}, // 8. Make X axis label black in colour. Set font size to 12px.
				   event: {
					click: function () {
						alert('<b>'+ this.series.name + '</b>');
					}
				   }

				
//				   formatter: function () {
//					return '<a href"' + this.value + '</a>'
//<a href="#" class="linkage-to-igv">{{rsid}}</a>
//return '<a href="' + categoryLinks[this.value] + '">' +
//                        this.value + '</a>';
				 }
		},
		series: []	
		};
	
	var GraphSeries = { name:"", data:[], point:{events:{click: null}} };

		        
	
	$(function () { // shorthand $() for $(document).ready()
		var chart;
		$(document).ready(function() { // jQuery object
					       // Run the code once the DOM is ready for JS code to execute
			samples=Str.find({},{fields:{_id:1}, sort:{_id:1}}).map(function (doc){return doc['_id']});
					     // Include _id field from the result object and sort the result by _id
			builtLobstr();
		});
	});
	
	Template.lobstr.onRendered(function() {
		builtLobstr();
	});

}

if (Meteor.isServer) {
	Meteor.publish('str',function() { // Publish a record set str
		return Str.find({});
	});
	Meteor.publish('samples',function() { // Publish a record set samples
		return Threshold.find({});
	});
	Meteor.publish('notes',function() { // Publish a record set notes
		return Notes.find({});
	});
	Meteor.methods({ // Defines functions that can be invoked over the network by clients.
		getResultsDir: function() {
			var path=Npm.require('path');
			return path.resolve('../../../../../../results');
		}
	});

}

Router.route('/', {
    template: 'home'
});
