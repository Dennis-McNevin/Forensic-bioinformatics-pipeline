Str=new Meteor.Collection('str');
Samples=new Meteor.Collection('samples');
Threshold=new Meteor.Collection('threshold');
CurrentView=new Meteor.Collection('currentview');
var sampleName;
var sampleFile;
var sample;
var samples;
var snps;
var layout='GlobalFiler';
var Schemas={};

Meteor.startup(function() {
})

Schemas.CurrentView=new SimpleSchema({
	sample: {
		type: String,
		max:300,
		autoform: {
			type: "selectize",
			options: function() {
				return _.uniq(Str.find({},{sort:{_id:1}}).fetch(),true,function(d) {return d.file}).map(function (c) { return {label:c.file,value:c.file+';'+c.orig}});
			}
		}
	},
	layout: {
		type: String,
		max: 50,
		autoform: {
			type: "selectize",
			options: function() {
				return _.map(["GlobalFiler","PowerPlex Fusion","PowerPlex 21","Promega CS7","Qiagen HDplex","Qiagen Argus X12","Y-Filer Plus","Y-Filer 17","PowerPlex Y-23"],function(c) {return {label:c,value:c};});
			}
		}
	}
});

CurrentView.attachSchema(Schemas.CurrentView);

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

Template.menu.events({
	'change #sampleSelect': function(e){
		console.log('Selected sample '+e.target.value);
		var values=e.target.value.split(';');
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

Session.setDefault('viz','lobstr');

Template.body.helpers({
	currentViz: function(){
		return Session.get('viz');
	}
})



Template.snptable.onCreated(function(){
	Session.set('snps',[]);
});

Template.snptable.helpers({
	snps: function() {
		return Session.get('snps');
	}
});

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
			Session.set('viz','lobstr');
			new Highcharts.Chart(graphOptions);
		}
	}else {
		sample=Str.findOne({_id:sampleName});
		if(sample!=null) {
			Session.set('snps',sample.snpsArray);
			Session.set('viz','snptable');
//			console.log(JSON.stringify(sample.snpsArray));
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
			AnalyticThresh="Analytic T: "+this.point.at+"%";
			StochasticThresh="Stochastic T: "+this.point.st+"%";
			StutterThresh="Stutter T: "+this.point.tt+"%";
			if(this.point.p<this.point.at) {
				AnalyticThresh='<font color="#0000ff"><b>'+AnalyticThresh+'</b></font>';
			}
			if(this.point.p<this.point.st) {
				StochasticThresh='<font color="#ff0000"><b>'+StochasticThresh+'</b></font>';
			}
			if(this.point.p<this.point.tt) {
				StutterThresh='<font color="#ff0000"><b>'+StutterThresh+'</b></font>';
			}
			return '<b>'+this.x+'</b> allele <b>'+this.series.name+'</b><br/>'+this.y+' read'+((this.y==1)?'':'s')+' <i>('+this.point.p+"%)</i><br/>Ref allele: "+this.point.r+"<br/>"+AnalyticThresh+"<br/>"+StochasticThresh+"<br/>"+StutterThresh;
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
						var region=coord[this.category];
						console.log("Clicked on "+p(this.category)+'. Opening '+region);
						var vcf=sampleFile.replace(".txt","").replace(".codis","").replace(".ystr","").replace(".snp","")+".vcf";
						var bam=vcf.replace("_lobstr.vcf","_sorted.bam");
						Meteor.call("getResultsDir", function(err, res) {
							var resultsDir=res;
							console.log('resultsDir='+resultsDir);
							window.open('http://localhost:60151/load?genome=hg19&merge=false&locus='+region+'&file=file://'+resultsDir+'/'+vcf+',file://'+resultsDir+'/'+bam+',file://'+resultsDir+'/../lobSTR_hg19.gff3');
						});
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
//console.log(chart_data);
	var chart = new Highcharts.Chart( chart_data );
	$('#container').show();
});
});

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
	Meteor.methods({
		getResultsDir: function() {
			var path=Npm.require('path');
			return path.resolve('../../../../../../results');
		}
	});
}

Router.route('/', {
    template: 'home'
});
