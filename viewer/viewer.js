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
var coordSNP={'rs798443': 'chr2:7968224-7968325',
		'rs11652805': 'chr17:62987100-62987201',
		'rs10497191': 'chr2:158667166-158667267',
		'rs16891982': 'chr5:33951642-33951743',
		'rs12439433': 'chr15:36219984-36220085'};
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

	
	Template._loginButtonsLoggedInDropdown.events({
	  'click #login-buttons-edit-profile': function(event) {
	    Router.go('profileEdit');
	  }
	});
	// Add an additional markup to the logged in dropdown
	// To edit the user's account or profile
	// Using package accounts-ui-bootstrap-3 
	

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
			var region=coordSNP[this.category];
			console.log("Clicked on "+p(this.category)+'. Opening '+region);
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
	
	Accounts.ui.config({
		passwordSignupFields: 'USERNAME_AND_EMAIL' // Display the email, username and password fields
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

// yAxis: [{ className: 'STRchartyAxisColour', title: {text: 'Read Counts'} }], // 8. Addding 'className' is not working
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
			 lineColor: '#000000',
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
	Meteor.startup(function(){ // To run code on both the client and server whe the application starts up
		Accounts.config({
    		sendVerificationEmail: false,
    		forbidClientAccountCreation: false
		});
	});
}

Router.route('/', {
    template: 'home'
});
