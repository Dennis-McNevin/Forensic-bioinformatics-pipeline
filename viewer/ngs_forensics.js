Str=new Meteor.Collection('str');
Samples=new Meteor.Collection('samples');
Threshold=new Meteor.Collection('threshold');
Notes=new Meteor.Collection('notes');
CurrentView=new Meteor.Collection('currentview');
var sampleName;
var sample;
var samples;
var layout='GlobalFiler';;
var Schemas={};
Meteor.startup(function() {
})

Schemas.CurrentView=new SimpleSchema({
	sample: {
		type: String,
		autoform: {
			type: "select",
			options: function() {
				return _.uniq(Str.find({},{sort:{_id:1}}).fetch(),true,function(d) {return d.file}).map(function (c) { return {label:c.file,value:c.file}});
			}
		}
	},
//	layout: {
//		type: String,
//		autoform: {
//			type: "select",
//			options: function() {
//				return _.map(["GlobalFiler","Y-Filer 17","Y-Filer Plus","PowerPlex Fusion","PowerPlex 21","PowerPlex Y-23","Qiagen Argus X12","Qiagen HDplex","Promega CS7"],function(c) {return {label:c,value:c};});
//			}
//		}
//	}
});
Schemas.Notes=new SimpleSchema({notes: {type: String}});

CurrentView.attachSchema(Schemas.CurrentView);
Notes.attachSchema(Schemas.Notes);

var coord={'TH01': 'chr11:2192319-2192345',
	'D13S317': 'chr13:82722161-82722203',
	'PentaE': 'chr15:97374246-97374269',
	'D16S539': 'chr16:86386309-86386351',
	'D18S51': 'chr18:60948901-60948971',
	'D21S11': 'chr21:20554292-20554417',
	'PentaD': 'chr21:45056087-45056150',
	'TPOX': 'chr2:1493426-1493456',
	'D3S1358': 'chr3:45582232-45582294',
	'FGA': 'chr4:155508889-155508975',
	'D5S818': 'chr5:123111251-123111293',
	'CSF1PO': 'chr5:149455888-149455938',
	'D7S820': 'chr7:83789543-83789593',
	'D8S1179': 'chr8:125907116-125907158',
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

if (Meteor.isClient) {

Meteor.subscribe("str");
Template.registerHelper("Schemas",Schemas);
AutoForm.setDefaultTemplate('materialize');

Template._loginButtonsLoggedInDropdown.events({
  'click #login-buttons-edit-profile': function(event) {
    Router.go('profileEdit');
  }
});

Template.currentView.events({
     'change select': function(e){
        console.log('Selected sample '+e.target.value);
     	sampleName=e.target.value;
     	layout=document.getElementById('layout').value;
        builtLobstr();
     }
});

Template.menu.events({
     'change form#menuForm #layout': function(e){
        console.log('Selected layout '+e.target.value);
     	layout=e.target.value;
        builtLobstr();
     }
 });
 
Template.snptable.helpers({
	snps: [
{rsid:'rs32314',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'6,4,4808,2798',refCount:10,altCount:7606},
{rsid:'rs174570',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'1621,1865,1755,1728',refCount:3486,altCount:3483},
{rsid:'rs192655',ref:'G',alt:'A',geno1:'A',geno2:'A',panel:'ai',depth:'1,1,639,733',refCount:2,altCount:1372},
{rsid:'rs260690',ref:'C',alt:'A',geno1:'A',geno2:'A',panel:'ai',depth:'0,0,1846,1437',refCount:0,altCount:3283},
{rsid:'rs316873',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'2698,803,2674,851',refCount:3501,altCount:3525},
{rsid:'rs385194',ref:'A',alt:'G',geno1:'A',geno2:'G',panel:'ai',depth:'1912,1460,1878,1376',refCount:3372,altCount:3254},
{rsid:'rs459920',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'2754,1273,2620,1370',refCount:4027,altCount:3990},
{rsid:'rs705308',ref:'C',alt:'A',geno1:'C',geno2:'A',panel:'ai',depth:'3472,927,2852,693',refCount:4399,altCount:3545},
{rsid:'rs734873',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1897,2065,1993,1873',refCount:3962,altCount:3866},
{rsid:'rs798443',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1367,1402,1413,1325',refCount:2769,altCount:2738},
{rsid:'rs818386',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'0,2,3739,3640',refCount:2,altCount:7379},
{rsid:'rs874299',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'1738,1797,2200,2227',refCount:3535,altCount:4427},
{rsid:'rs946918',ref:'G',alt:'T',geno1:'G',geno2:'T',panel:'ai',depth:'2327,1644,2314,1680',refCount:3971,altCount:3994},
{rsid:'rs1040045',ref:'G',alt:'A',geno1:'A',geno2:'A',panel:'ai',depth:'3,2,2117,2338',refCount:5,altCount:4455},
{rsid:'rs1040404',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'805,813,845,649',refCount:1618,altCount:1494},
{rsid:'rs1229984',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'1,5,3470,3241',refCount:6,altCount:6711},
{rsid:'rs1462906',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'0,0,2972,3585',refCount:0,altCount:6557},
{rsid:'rs1471939',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'0,2,1009,2442',refCount:2,altCount:3451},
{rsid:'rs1569175',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'1,0,1267,933',refCount:1,altCount:2200},
{rsid:'rs1572018',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'1,1,954,979',refCount:2,altCount:1933},
{rsid:'rs1879488',ref:'A',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'0,0,1698,3003',refCount:0,altCount:4701},
{rsid:'rs1950993',ref:'G',alt:'T',geno1:'G',geno2:'T',panel:'ai',depth:'831,608,582,469',refCount:1439,altCount:1051},
{rsid:'rs2070586',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'2353,1783,2111,1743',refCount:4136,altCount:3854},
{rsid:'rs2357442',ref:'A',alt:'C',geno1:'A',geno2:'C',panel:'ai',depth:'1723,2147,1754,2032',refCount:3870,altCount:3786},
{rsid:'rs2416791',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'1,1,3448,2156',refCount:2,altCount:5604},
{rsid:'rs2504853',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'2894,1198,2739,1173',refCount:4092,altCount:3912},
{rsid:'rs2835370',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'14,4,5533,2456',refCount:18,altCount:7989},
{rsid:'rs2946788',ref:'G',alt:'T',geno1:'G',geno2:'T',panel:'ai',depth:'2657,1234,2320,1196',refCount:3891,altCount:3516},
{rsid:'rs2966849',ref:'A',alt:'G',geno1:'A',geno2:'G',panel:'ai',depth:'1944,1733,1639,1529',refCount:3677,altCount:3168},
{rsid:'rs3745099',ref:'G',alt:'A',geno1:'A',geno2:'A',panel:'ai',depth:'6,6,5815,1579',refCount:12,altCount:7394},
{rsid:'rs3793791',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'6,7,4926,3064',refCount:13,altCount:7990},
{rsid:'rs3916235',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'0,0,2324,449',refCount:0,altCount:2773},
{rsid:'rs4666200',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'3099,902,3078,912',refCount:4001,altCount:3990},
{rsid:'rs4798812',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'2296,1745,2029,1751',refCount:4041,altCount:3780},
{rsid:'rs4891825',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1776,1769,1844,1745',refCount:3545,altCount:3589},
{rsid:'rs4908343',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'719,620,707,664',refCount:1339,altCount:1371},
{rsid:'rs4918842',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'2985,978,3045,908',refCount:3963,altCount:3953},
{rsid:'rs4984913',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'1,0,7829,95',refCount:1,altCount:7924},
{rsid:'rs6451722',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1244,2586,1013,2018',refCount:3830,altCount:3031},
{rsid:'rs6541030',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'5,2,5955,1916',refCount:7,altCount:7871},
{rsid:'rs6548616',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'780,827,1036,998',refCount:1607,altCount:2034},
{rsid:'rs6556352',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'907,1487,796,1276',refCount:2394,altCount:2072},
{rsid:'rs7421394',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'1,0,5303,2656',refCount:1,altCount:7959},
{rsid:'rs7554936',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'9,2,6270,1735',refCount:11,altCount:8005},
{rsid:'rs7722456',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'0,0,3791,3828',refCount:0,altCount:7619},
{rsid:'rs7745461',ref:'A',alt:'G',geno1:'A',geno2:'G',panel:'ai',depth:'1616,1661,1707,1605',refCount:3277,altCount:3312},
{rsid:'rs7803075',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'5,0,5659,1476',refCount:5,altCount:7135},
{rsid:'rs7844723',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'1264,1050,1230,1006',refCount:2314,altCount:2236},
{rsid:'rs7997709',ref:'C',alt:'T',geno1:'T',geno2:'T',panel:'ai',depth:'0,0,2138,2054',refCount:0,altCount:4192},
{rsid:'rs8035124',ref:'A',alt:'C',geno1:'A',geno2:'C',panel:'ai',depth:'2898,1874,2001,1242',refCount:4772,altCount:3243},
{rsid:'rs9522149',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'2,1,3092,4366',refCount:3,altCount:7458},
{rsid:'rs9530435',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'0,0,4729,1661',refCount:0,altCount:6390},
{rsid:'rs9809104',ref:'T',alt:'C',geno1:'T',geno2:'C',panel:'ai',depth:'1703,1654,1616,1719',refCount:3357,altCount:3335},
{rsid:'rs9845457',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1162,1380,2260,1586',refCount:2542,altCount:3846},
{rsid:'rs10007810',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'1358,1339,773,857',refCount:2697,altCount:1630},
{rsid:'rs10497191',ref:'T',alt:'C',geno1:'C',geno2:'C',panel:'ai',depth:'2,0,3901,4109',refCount:2,altCount:8010},
{rsid:'rs10512572',ref:'G',alt:'A',geno1:'G',geno2:'A',panel:'ai',depth:'943,714,941,721',refCount:1657,altCount:1662},
{rsid:'rs10839880',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'942,941,963,881',refCount:1883,altCount:1844},
{rsid:'rs11652805',ref:'C',alt:'T',geno1:'C',geno2:'T',panel:'ai',depth:'1061,703,1035,749',refCount:1764,altCount:1784},
{rsid:'rs12544346',ref:'G',alt:'A',geno1:'A',geno2:'A',panel:'ai',depth:'0,0,4942,3061',refCount:0,altCount:8003},
{rsid:'rs12913832',ref:'A',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'2,2,4676,3135',refCount:4,altCount:7811},
{rsid:'rs16891982',ref:'C',alt:'G',geno1:'G',geno2:'G',panel:'ai',depth:'0,0,1432,1578',refCount:0,altCount:3010} ]
});

var SnpOptions = {
        chart: {
            type: 'column'
        },

        title: {
            text: 'rs13218840'
        },

        xAxis: {
            categories: ['rs13218840']
        },

        yAxis: {
            allowDecimals: false,
            min: 0,
            title: {
                text: 'Number of fruits'
            }
        },

        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    this.series.name + ': ' + this.y + '<br/>' +
                    'Total: ' + this.point.stackTotal;
            }
        },

        plotOptions: {
            column: {
                stacking: 'normal'
            }
        },

        series: [{
            name: 'A1',
            data: [2],
            stack: 'A'
        }, {
            name: 'A2',
            data: [3],
            stack: 'A'
        }, {
            name: 'T',
            data: [7],
            stack: 'T'
        }]
    };

var SnpSeries = {
        name:"",
        data:[],
        point:{events:{click: null}}
};

Template.snptable.events({
	'mouseover [data-toggle="popover"]': function(e){
		var p = $(e.currentTarget).popover({
			html:true
		});
	var cTarget=e.currentTarget;
	var chart = new Highcharts.Chart({
        chart: {
            renderTo: cTarget.id+'con',
            type: 'column'
        },
        plotOptions: {
            column: {
                dataLabels: { enabled: true }
            }
        },
        title:{text:null},
        legend:{enabled:false},
        credits:{enabled:false},
        xAxis: {
        	categories: [cTarget.getAttribute("ref"),cTarget.getAttribute("alt")]	
        },
        yAxis: {
            title: {
                text: 'reads',
                useHTML: true,
                style: {
                    "-webkit-transform": "rotate(90deg)",
                    "-moz-transform": "rotate(90deg)", 
                    "-o-transform": "rotate(90deg)"
                }
            }
        },
        series: [{ name:'reads', data: [+cTarget.getAttribute("refC"),+cTarget.getAttribute("altC")] }]
    });
	}
});

Accounts.ui.config({
    requestPermissions: {},
    extraSignupFields: [{
        fieldName: 'first-name',
        fieldLabel: 'First name',
        inputType: 'text',
        visible: true,
        validate: function(value, errorFunction) {
          if (!value) {
            errorFunction("Please write your first name");
            return false;
          } else {
            return true;
          }
        }
    }, {
        fieldName: 'last-name',
        fieldLabel: 'Last name',
        inputType: 'text',
        visible: true,
    }, {
        fieldName: 'gender',
        showFieldLabel: false,      // If true, fieldLabel will be shown before radio group
        fieldLabel: 'Gender',
        inputType: 'radio',
        radioLayout: 'vertical',    // It can be 'inline' or 'vertical'
        data: [{                    // Array of radio options, all properties are required
            id: 1,                  // id suffix of the radio element
            label: 'Male',          // label for the radio element
            value: 'm'              // value of the radio element, this will be saved.
          }, {
            id: 2,
            label: 'Female',
            value: 'f',
            checked: 'checked'
        }],
        visible: true
    }, {
        fieldName: 'country',
        fieldLabel: 'Country',
        inputType: 'select',
        showFieldLabel: true,
        empty: 'Please select your country of residence',
        data: [{
            id: 1,
            label: 'Australia',
            value: 'au'
          }, {
            id: 2,
            label: 'New Zealand',
            value: 'nz',
          }, {
            id: 3,
            label: 'United Kingdom',
            value: 'uk',
          }, {
            id: 4,
            label: 'United States',
            value: 'us',
        }],
        visible: true
    }, {
        fieldName: 'terms',
        fieldLabel: 'I accept the terms and conditions',
        inputType: 'checkbox',
        visible: true,
        saveToProfile: false,
        validate: function(value, errorFunction) {
            if (value) {
                return true;
            } else {
                errorFunction('You must accept the terms and conditions.');
                return false;
            }
        }
    }]
});


function builtLobstr(collection) {
//	samples=Str.find({},{ sort:{_id:1}}).map(function (doc){return doc['sample']});
//	samples=_.uniq(Str.find({},{sort:{_id:1}}).fetch(),true,function(d) {return d.file});
//	console.log('samples: '+p(samples)); fields:{_id:1,type:1},
//	console.log('sampleName: '+p(sampleName));
	sample=Str.findOne({_id:sampleName+'|'+layout});
	sampleType=typeof sample;
//	console.log('sample('+p(sampleType)+'): '+p(sample));
	if(sampleType!='undefined') {
		for(x = 0; x < 8; x++) {
			if(typeof sample.categoriesArray[x]=='undefined' || sample.categoriesArray[x].length<1) {
				$('#containerChart'+x).hide();
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
			new Highcharts.Chart(graphOptions);
		}
	}
}


var GraphOptions = {
    chart: { type: 'column', renderTo: 'containerChart0' },
	title:{ text:null },
	subtitle:{ text:null },
	credits: { enabled: false },
    legend: { enabled: false },
    exporting:{enabled: false},
	tooltip: { formatter: function () {
		if(this.y>0) {
			PrimaryThresh="Threshold: "+this.point.pt+"%";
			StutterThresh="Stutter T: "+this.point.st+"%";
			if(this.point.p<this.point.pt) {
				PrimaryThresh='<font color="#0000ff"><b>'+PrimaryThresh+'</b></font>';
			}
			if(this.point.p<this.point.st) {
				StutterThresh='<font color="#ff0000"><b>'+StutterThresh+'</b></font>';
			}
			return '<b>'+this.x+'</b><br/>Allele <b>'+this.series.name+'</b><br/>'+this.y+' read'+((this.y==1)?'':'s')+' <i>('+this.point.p+"%)</i><br/>Ref allele: "+this.point.r+"<br/>"+PrimaryThresh+"<br/>"+StutterThresh;
		}
	} },
	plotOptions: {
		column: {
			dataLabels: {
				enabled: true,
				formatter: function(){ return this.point.l; },
				style:{ fontSize:'8pt', color:'#101010', },
				x:0,
				y:0,
				align:'center'
			},
		},
		series: { 
			maxPointWidth: 30,
			point: {
				events: {
					click: function(e) {
						console.log("Clicked on "+p(this.category)+'. Opening '+coord[this.category]);
						var vcf=sampleName.replace(".codis","").replace(".ystr","")+".vcf";
						var bam=vcf.replace("_lobstr.vcf",".bam");
						window.open('http://localhost:60151/load?genome=hg19&merge=false&locus='+coord[this.category]+'&file=file:///home/ngsforensics/results/'+vcf+',file:///home/ngsforensics/results/'+bam+',file:///home/ngsforensics/forensicsapp/ngs_forensics/data/lobSTR_hg19.gff3');
//						hs.htmlExpand(null, {
//                                    pageOrigin: {
//                                        x: e.pageX || e.clientX,
//                                        y: e.pageY || e.clientY
//                                    },
//                                    headingText: e.target.category,
//                                    maincontentText: 'blah blah',
//                                    width: 200
//                                });
					}
				}
			}
		}
	},
	yAxis: { min:0, title:{text:'Read Counts'}, labels:{overflow:'justify'} },
	xAxis: { categories: [] },
	series: []	
};

var GraphSeries = { name:"", data:[], point:{events:{click: null}} };

$(function () {
	var chart;
	$(document).ready(function() {
//		samples=Str.find({},{fields:{_id:1}, sort:{_id:1}}).map(function (doc){return doc['_id']});
//		builtLobstr();
    });
    $('[data-toggle="popover"]').popover({
    content: "<div id='container' style='min-width: 400px;display:none; height: 400px; margin: 0'></div>",
    html: true
}).click(function() {
var chart_data = getChartData();
console.log(chart_data);
	var chart = new Highcharts.Chart( chart_data );
        $('#container').show();
});
});

   function getChartData(){
        return{
            chart:{
            renderTo:'Austin2'},
        title: {
            text: 'Monthly Average Temperature',
            x: -20 //center
        },
        subtitle: {
            text: 'Source: WorldClimate.com',
            x: -20
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        },
        yAxis: {
            title: {
                text: 'Temperature (°C)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: '°C'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: 'Tokyo',
            data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
        }, {
            name: 'New York',
            data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
        }, {
            name: 'Berlin',
            data: [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
        }, {
            name: 'London',
            data: [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
        }]
    } ;
}

Template.lobstr.onRendered(function() {
	builtLobstr();
});


}

if (Meteor.isServer) {
	Meteor.publish('str',function() {
		return Str.find({});
	});
	Meteor.publish('samples',function() {
		return Threshold.find({});
	});
}

Router.route('/', {
    template: 'home'
});
