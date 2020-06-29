import django.test
from creatives.models import Creative
from creative_groups.models import CreativeGroup


class TestCreativeCreation(django.test.TestCase):

    def setUp(self):

        self.maxDiff = None

        CreativeGroup.objects.create(name='cg')

        #  DCM INS
        Creative.objects.create(name='DCM_INS',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <ins class='dcmads' style='display:inline-block;width:160px;height:600px'
                                    data-dcm-placement='N3926.1172840.ADTHEORENTINC/B23165039.254809319'
                                    data-dcm-rendering-mode='script'
                                    data-dcm-https-only
                                    data-dcm-resettable-device-id=''
                                    data-dcm-app-id=''>
                                  <script src='https://www.googletagservices.com/dcm/dcmads.js'></script>
                                </ins>
                                ''')

        #  DCM INS IAS BLOCKING
        Creative.objects.create(name='DCM_INS_IAS_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <ins class='dcmads' style='display:inline-block;width:160px;height:600px'
                                    data-dcm-placement='N4427.1172840.ADTHEORENTINC/B23519098.267458228'
                                    data-dcm-rendering-mode='script'
                                    data-dcm-https-only
                                    data-dcm-resettable-device-id=''
                                    data-dcm-app-id=''>
                                  <script src='https://fw.adsafeprotected.com/rjss/www.googletagservices.com/381334/46753071/dcm/dcmads.js'></script>
                                </ins>
                                ''')

        #  DCM INS IAS MONITORING
        Creative.objects.create(name='DCM_INS_IAS_MONITORING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <ins class='dcmads' style='display:inline-block;width:160px;height:600px'
                                    data-dcm-placement='N3926.1172840.ADTHEORENTINC/B23165039.254809319'
                                    data-dcm-rendering-mode='script'
                                    data-dcm-https-only
                                    data-dcm-resettable-device-id=''
                                    data-dcm-app-id=''>
                                  <script src='https://www.googletagservices.com/dcm/dcmads.js'></script>
                                </ins><SCRIPT TYPE="application/javascript" SRC="https://pixel.adsafeprotected.com/rjss/st/326369/38911877/skeleton.js"></SCRIPT> 
                                <NOSCRIPT><IMG SRC="https://pixel.adsafeprotected.com/rfw/st/326369/38911876/skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>
                                ''')

        #  DCM INS DV BLOCKING
        Creative.objects.create(name='DCM_INS_DV_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script type="text/adtag">
                                <ins class='dcmads' style='display:inline-block;width:728px;height:90px'
                                    data-dcm-placement='N30602.1172840ADTHEORENTINC1/B23952138.275863207'
                                    data-dcm-rendering-mode='script'
                                    data-dcm-https-only
                                    data-dcm-resettable-device-id=''
                                    data-dcm-app-id=''>
                                  <script src='https://www.googletagservices.com/dcm/dcmads.js'></scr+ipt>
                                </ins>
                                </script>
                                <script language="javascript" type="text/javascript" src="https://cdn.doubleverify.com/dvbs_src.js?ctx=15896033&cmp=23952138&plc=275863207&sid=3162285&dvregion=0&unit=728x90">
                                </script>
                                ''')

        #  DCM LEGACY
        Creative.objects.create(name='DCM_LEGACY',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <SCRIPT language='JavaScript1.1' SRC="https://ad.doubleclick.net/ddm/adj/N3926.1172840.ADTHEORENTINC/B23165039.254807933;sz=300x250;ord=[timestamp];dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=?">
                                </SCRIPT>
                                ''')

        #  DCM LEGACY IAS MONITORING
        Creative.objects.create(name='DCM_LEGACY_IAS_MONITORING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <SCRIPT language='JavaScript1.1' SRC="https://ad.doubleclick.net/ddm/adj/N3926.1172840.ADTHEORENTINC/B23165039.254807933;sz=300x250;ord=[timestamp];dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=?">
                                </SCRIPT>
                                <SCRIPT TYPE="application/javascript" SRC="https://pixel.adsafeprotected.com/rjss/st/326369/38911871/skeleton.js"></SCRIPT> <NOSCRIPT><IMG SRC="https://pixel.adsafeprotected.com/rfw/st/326369/38911870/skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>
                                ''')

        #  DCM LEGACY DV BLOCKING
        Creative.objects.create(name='DCM_LEGACY_DV_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script type="text/adtag">
                                <script language='JavaScript1.1' SRC="https://ad.doubleclick.net/ddm/adj/N3926.1172840.ADTHEORENTINC/B23165039.254807933;sz=300x250;ord=[timestamp];dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=?">
                                </scr+ipt>
                                <script language="javascript" type="text/javascript" src="https://cdn.doubleverify.com/dvbs_src.js?ctx=15896033&cmp=23952138&plc=275863207&sid=3162285&dvregion=0&unit=728x90">
                                </script>
                                ''')

        #  SIZMEK IAS BLOCKING
        Creative.objects.create(name='SIZMEK_IAS_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script src="https://fw.adsafeprotected.com/rjss/bs.serving-sys.com/361042/46613318/Serving/adServer.bs?c=28&cn=display&pli=1075099860&w=300&h=600&ord=[timestamp]&z=0"></script>
                                <noscript>
                                <a href="https://bs.serving-sys.com/Serving/adServer.bs?cn=brd&pli=1075099860&Page=&Pos=1474389399" target="_blank">
                                <img src="https://fw.adsafeprotected.com/rfw/bs.serving-sys.com/361042/46613317/Serving/adServer.bs?c=8&cn=display&pli=1075099860&Page=&Pos=1474389399" border=0 width=300 height=600></a>
                                </noscript>
                                ''')

        #  SIZMEK IAS MONITORING
        Creative.objects.create(name='SIZMEK_IAS_MONITORING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=rsb&c=28&pli=29467096&PluID=0&w=320&h=50&ord=[timestamp]&ucm=true&ebaddid=$$[IDFA]$$&ebgaid=$$[IDFA]$$&ebidfar=$$[IDFA]$$&ebidfas1=$$[IDFA]$$&ebidfas2=$$[IDFA]$$&ebidfam=$$[IDFA]$$&ebwaid=$$[IDFA]$$&ebappid=$$[PUBLISHERID]$$&ebappname=$$[ENCODEDPAGEURL]$$&ebmblat=$$[LATITUDE]$$&ebmblong=$$[LONGITUDE]$$"></script>
                                <noscript>
                                <a href="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=brd&FlightID=29467096&Page=&PluID=0&Pos=1761343217&ebaddid=$$[IDFA]$$&ebgaid=$$[IDFA]$$&ebidfar=$$[IDFA]$$&ebidfas1=$$[IDFA]$$&ebidfas2=$$[IDFA]$$&ebidfam=$$[IDFA]$$&ebwaid=$$[IDFA]$$&ebappid=$$[PUBLISHERID]$$&ebappname=$$[ENCODEDPAGEURL]$$&ebmblat=$$[LATITUDE]$$&ebmblong=$$[LONGITUDE]$$" target="_blank"><img src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=bsr&FlightID=29467096&Page=&PluID=0&Pos=1761343217&ebaddid=$$[IDFA]$$&ebgaid=$$[IDFA]$$&ebidfar=$$[IDFA]$$&ebidfas1=$$[IDFA]$$&ebidfas2=$$[IDFA]$$&ebidfam=$$[IDFA]$$&ebwaid=$$[IDFA]$$&ebappid=$$[PUBLISHERID]$$&ebappname=$$[ENCODEDPAGEURL]$$&ebmblat=$$[LATITUDE]$$&ebmblong=$$[LONGITUDE]$$" border=0 width=320 height=50></a>
                                </noscript>
                                <SCRIPT TYPE="application/javascript" SRC="https://pixel.adsafeprotected.com/rjss/st/393820/42587791/skeleton.js"></SCRIPT> <NOSCRIPT><IMG SRC="https://pixel.adsafeprotected.com/rfw/st/393820/42587790/skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>
                                        ''')

        #  SIZMEK DV BLOCKING
        Creative.objects.create(name='SIZMEK_DV_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script type="text/adtag">
                                <script src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=rsb&c=28&pli=28887076&PluID=0&w=300&h=250&ucm=true&ncu=$$[ENCODEDCLICKURL]/images/invisible.gif$$&ord=[timestamp]&ucm=true"></scr+ipt><noscript><a href="[CLICKURL]https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=brd&FlightID=28887076&Page=&PluID=0&Pos=1120116384" target="_blank"><img src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=bsr&FlightID=28887076&Page=&PluID=0&Pos=1120116384" border=0 width=300 height=250></a></noscript>
                                </script>
                                <script language="javascript" type="text/javascript" src="https://cdn.doubleverify.com/dvbs_src.js?ctx=3261584&cmp=986937&plc=28887076&sid=67914&dvregion=2&unit=300x250">
                                </script>
                                ''')

        #  SIZMEK
        Creative.objects.create(name='SIZMEK',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                <script src="https://bs.serving-sys.com/Serving/adServer.bs?c=28&cn=display&pli=1075557611&w=728&h=90&ord=[timestamp]&z=0"></script>
                                <noscript>
                                <a href="https://bs.serving-sys.com/Serving/adServer.bs?cn=brd&pli=1075557611&Page=&Pos=1002791316" target="_blank">
                                <img src="https://bs.serving-sys.com/Serving/adServer.bs?c=8&cn=display&pli=1075557611&Page=&Pos=1002791316" border=0 width=728 height=90></a>
                                </noscript>
                                ''')

        #  FLASHTALKING
        Creative.objects.create(name='FLASHTALKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                        <noscript>
                                        <a href="https://servedby.flashtalking.com/click/8/119966;4679546;0;209;0/?ft_width=300&ft_height=250&url=27893134" target="_blank">
                                        <img border="0" src="https://servedby.flashtalking.com/imp/8/119966;4679546;205;gif;AdTheorentUS;AdTheorentDotComDisplay1TrialBondcatchallCROSSACQPROSNACPMNANA300x250/?"></a>
                                        </noscript>
                                        <script language="Javascript1.1" type="text/javascript">
                                        var ftKeyword = "4679546__[LINEITEMID]";
                                        var ftKW = (ftKeyword) ? '&ft_keyword=' +encodeURIComponent(ftKeyword) : "";
                                        var ftSection = (ftKeyword) ? encodeURIComponent(ftKeyword) : "";
                                        
                                        var ftClick = "";
                                        var ftLat = "[LATITUDE] ";
                                        var ftLong = "[LONGITUDE]";
                                        var ftLatLong = "&ft_lat="+encodeURIComponent(ftLat)+"&ft_long="+encodeURIComponent(ftLong);
                                        var ftExpTrack_4679546 = "";
                                        var ftX = "";
                                        var ftY = "";
                                        var ftZ = "";
                                        var ftOBA = 1;
                                        var ftContent = "";
                                        var ftCustom = "[TIMESTAMP]";
                                        var ft300x250_OOBclickTrack = "";
                                        var ftRandom = Math.random()*1000000;
                                        var ftBuildTag1 = "<scr";
                                        var ftBuildTag2 = "</";
                                        var ftClick_4679546 = ftClick;
                                        if(typeof(ft_referrer)=="undefined"){var ft_referrer=(function(){var r="";if(window==top){r=window.location.href;}else{try{r=window.parent.location.href;}catch(e){}r=(r)?r:document.referrer;}while(encodeURIComponent(r).length>1000){r=r.substring(0,r.length-1);}return r;}());}
                                        var ftDomain = (window==top)?"":(function(){var d=document.referrer,h=(d)?d.match("(?::q/q/)+([qw-]+(q.[qw-]+)+)(q/)?".replace(/q/g,decodeURIComponent("%"+"5C")))[1]:"";return (h&&h!=location.host)?"&ft_ifb=1&ft_domain="+encodeURIComponent(h):"";}());
                                        var ftTag = ftBuildTag1 + 'ipt language="javascript1.1" type="text/javascript" ';
                                        ftTag += 'src="https://servedby.flashtalking.com/imp/8/119966;4679546;201;js;AdTheorentUS;AdTheorentDotComDisplay1TrialBondcatchallCROSSACQPROSNACPMNANA300x250/?ftx='+ftX+'&fty='+ftY+'&ftadz='+ftZ+'&ftscw='+ftContent+'&ft_custom='+ftCustom+'&ft_section='+ftSection+'&ftOBA='+ftOBA+ftDomain+'&ft_agentEnv='+(window.mraid||window.ormma?'1':'0')+ftLatLong+'&ft_referrer='+encodeURIComponent(ft_referrer)+ftKW+'&cachebuster='+ftRandom+'" id="ftscript_300x250" name="ftscript_300x250"';
                                        ftTag += '>' + ftBuildTag2 + 'script>';
                                        document.write(ftTag);
                                        </script>
                                        ''')

        #  FLASHTALKING IAS BLOCKING
        Creative.objects.create(name='FLASHTALKING_IAS_BLOCKING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                        <noscript>
                                        <a href="https://servedby.flashtalking.com/click/8/120033;4361859;0;209;0/?ft_width=160&ft_height=600&url=26606754" target="_blank">
                                        <img border="0" src="https://fw.adsafeprotected.com/rfw/servedby.flashtalking.com/354927/42478640/imp/8/120033;4361859;205;gif;AdTheorentUS;P14ZSBWWALACU019AudienceXAXISNATDISCTNDSKBANMWSTDBANGMEN1CPMPLCMDCM160X600ADPAPRunofNetworkDemoF30491x1StandardFlashtalkingNA/?"></a>
                                        </noscript>
                                        <script language="Javascript1.1" type="text/javascript">
                                        var ftKeyword = "INSERT AD GROUP MACRO HERE";
                                        var ftKW = (ftKeyword) ? '&ft_keyword=' +encodeURIComponent(ftKeyword) : "";
                                        var ftSection = (ftKeyword) ? encodeURIComponent(ftKeyword) : "";
                                        
                                        var ftClick = "";
                                        var ftLat = "[LATITUDE] ";
                                        var ftLong = "[LONGITUDE]";
                                        var ftLatLong = "&ft_lat="+encodeURIComponent(ftLat)+"&ft_long="+encodeURIComponent(ftLong);
                                        var ftExpTrack_4361859 = "";
                                        var ftX = "";
                                        var ftY = "";
                                        var ftZ = "";
                                        var ftOBA = 1;
                                        var ftContent = "";
                                        var ftCustom = "";
                                        var ftID = function(){for(var e=["[IDFA]"],a=e.length,r="";a--;)if(e[a]&&!RegExp("[^a-z0-9"+decodeURIComponent("%"+"5C")+"-]","i").test(e[a])){r=e[a];break}return r}();
                                        var ft160x600_OOBclickTrack = "";
                                        var ftRandom = Math.random()*1000000;
                                        var ftBuildTag1 = "<scr";
                                        var ftBuildTag2 = "</";
                                        var ftClick_4361859 = ftClick;
                                        if(typeof(ft_referrer)=="undefined"){var ft_referrer=(function(){var r="";if(window==top){r=window.location.href;}else{try{r=window.parent.location.href;}catch(e){}r=(r)?r:document.referrer;}while(encodeURIComponent(r).length>1000){r=r.substring(0,r.length-1);}return r;}());}
                                        var ftDomain = (window==top)?"":(function(){var d=document.referrer,h=(d)?d.match("(?::q/q/)+([qw-]+(q.[qw-]+)+)(q/)?".replace(/q/g,decodeURIComponent("%"+"5C")))[1]:"";return (h&&h!=location.host)?"&ft_ifb=1&ft_domain="+encodeURIComponent(h):"";}());
                                        var ftTag = ftBuildTag1 + 'ipt language="javascript1.1" type="text/javascript" ';
                                        ftTag += 'src="https://fw.adsafeprotected.com/rjss/servedby.flashtalking.com/354927/42478641/imp/8/120033;4361859;201;js;AdTheorentUS;P14ZSBWWALACU019AudienceXAXISNATDISCTNDSKBANMWSTDBANGMEN1CPMPLCMDCM160X600ADPAPRunofNetworkDemoF30491x1StandardFlashtalkingNA/?ftx='+ftX+'&fty='+ftY+'&ftadz='+ftZ+'&ftscw='+ftContent+'&ft_custom='+ftCustom+'&ft_section='+ftSection+'&ft_id='+ftID+'&ftOBA='+ftOBA+ftDomain+'&ft_agentEnv='+(window.mraid||window.ormma?'1':'0')+ftLatLong+'&ft_referrer='+encodeURIComponent(ft_referrer)+ftKW+'&cachebuster='+ftRandom+'" id="ftscript_160x600" name="ftscript_160x600"';
                                        ftTag += '>' + ftBuildTag2 + 'script>';
                                        document.write(ftTag);
                                        </script>
                                        ''')

        #  FLASHTALKING IAS MONITORING
        Creative.objects.create(name='FLASHTALKING_IAS_MONITORING',
                                creative_group_id=CreativeGroup.objects.get(name='cg'),
                                markup='''
                                        <noscript>
                                        <a href="https://servedby.flashtalking.com/click/8/118079;4715457;0;209;0/?ft_width=320&ft_height=50&url=28031228" target="_blank">
                                        <img border="0" src="https://servedby.flashtalking.com/imp/8/118079;4715457;205;gif;AdTheorentUS;2019Q4CTCPHELPLINEENGLISHAdTheorentCADisplay3PSmokersMULTI320x50NicotinePatchSideStaticFT/?"></a>
                                        </noscript>
                                        <script language="Javascript1.1" type="text/javascript">
                                        var ftClick = "";
                                        var ftLat = "[LATITUDE] ";
                                        var ftLong = "[LONGITUDE]";
                                        var ftLatLong = "&ft_lat="+encodeURIComponent(ftLat)+"&ft_long="+encodeURIComponent(ftLong);
                                        var ftExpTrack_4715457 = "";
                                        var ftX = "";
                                        var ftY = "";
                                        var ftZ = "";
                                        var ftOBA = 1;
                                        var ftContent = "";
                                        var ftCustom = "";
                                        var ft320x50_OOBclickTrack = "";
                                        var ftRandom = Math.random()*1000000;
                                        var ftBuildTag1 = "<scr";
                                        var ftBuildTag2 = "</";
                                        var ftClick_4715457 = ftClick;
                                        if(typeof(ft_referrer)=="undefined"){var ft_referrer=(function(){var r="";if(window==top){r=window.location.href;}else{try{r=window.parent.location.href;}catch(e){}r=(r)?r:document.referrer;}while(encodeURIComponent(r).length>1000){r=r.substring(0,r.length-1);}return r;}());}
                                        var ftDomain = (window==top)?"":(function(){var d=document.referrer,h=(d)?d.match("(?::q/q/)+([qw-]+(q.[qw-]+)+)(q/)?".replace(/q/g,decodeURIComponent("%"+"5C")))[1]:"";return (h&&h!=location.host)?"&ft_ifb=1&ft_domain="+encodeURIComponent(h):"";}());
                                        var ftTag = ftBuildTag1 + 'ipt language="javascript1.1" type="text/javascript" ';
                                        ftTag += 'src="https://servedby.flashtalking.com/imp/8/118079;4715457;201;js;AdTheorentUS;2019Q4CTCPHELPLINEENGLISHAdTheorentCADisplay3PSmokersMULTI320x50NicotinePatchSideStaticFT/?ftx='+ftX+'&fty='+ftY+'&ftadz='+ftZ+'&ftscw='+ftContent+'&ft_custom='+ftCustom+'&ftOBA='+ftOBA+ftDomain+'&ft_agentEnv='+(window.mraid||window.ormma?'1':'0')+ftLatLong+'&ft_referrer='+encodeURIComponent(ft_referrer)+'&cachebuster='+ftRandom+'" id="ftscript_320x50" name="ftscript_320x50"';
                                        ftTag += '>' + ftBuildTag2 + 'script>';
                                        document.write(ftTag);
                                        </script>
                                        
                                        
<SCRIPT TYPE="application/javascript" SRC="https://pixel.adsafeprotected.com/rjss/st/371151/46467106/skeleton.js"></SCRIPT> <NOSCRIPT><IMG SRC="https://pixel.adsafeprotected.com/rfw/st/371151/46467105/skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>
                                        ''')

    def test_clean_up(self):

        dcm_ins = Creative.objects.get(name='DCM_INS')
        dcm_ins_ias_blocking = Creative.objects.get(name='DCM_INS_IAS_BLOCKING')
        dcm_ins_ias_monitoring = Creative.objects.get(name='DCM_INS_IAS_MONITORING')
        dcm_ins_dv_blocking = Creative.objects.get(name='DCM_INS_DV_BLOCKING')
        dcm_legacy = Creative.objects.get(name='DCM_LEGACY')
        dcm_legacy_ias_monitoring = Creative.objects.get(name='DCM_LEGACY_IAS_MONITORING')
        dcm_legacy_dv_blocking = Creative.objects.get(name='DCM_LEGACY_DV_BLOCKING')
        sizmek_ias_blocking = Creative.objects.get(name='SIZMEK_IAS_BLOCKING')
        sizmek_ias_monitoring = Creative.objects.get(name='SIZMEK_IAS_MONITORING')
        sizmek_dv_blocking = Creative.objects.get(name='SIZMEK_DV_BLOCKING')
        sizmek = Creative.objects.get(name='SIZMEK')
        flashtalking = Creative.objects.get(name='FLASHTALKING')
        flashtalking_ias_blocking = Creative.objects.get(name='FLASHTALKING_IAS_BLOCKING')
        flashtalking_ias_monitoring = Creative.objects.get(name='FLASHTALKING_IAS_MONITORING')

        self.assertEqual(dcm_ins.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_ins_ias_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_ins_ias_monitoring.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_ins_dv_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_legacy.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_legacy_ias_monitoring.markup.find('_x000D_'), -1)
        self.assertEqual(dcm_legacy_dv_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(sizmek_ias_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(sizmek_ias_monitoring.markup.find('_x000D_'), -1)
        self.assertEqual(sizmek_dv_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(sizmek.markup.find('_x000D_'), -1)
        self.assertEqual(flashtalking.markup.find('_x000D_'), -1)
        self.assertEqual(flashtalking_ias_blocking.markup.find('_x000D_'), -1)
        self.assertEqual(flashtalking_ias_monitoring.markup.find('_x000D_'), -1)

    def test_determine_ad_server(self):

        dcm_ins = Creative.objects.get(name='DCM_INS')
        dcm_ins_ias_blocking = Creative.objects.get(name='DCM_INS_IAS_BLOCKING')
        dcm_ins_ias_monitoring = Creative.objects.get(name='DCM_INS_IAS_MONITORING')
        dcm_ins_dv_blocking = Creative.objects.get(name='DCM_INS_DV_BLOCKING')
        dcm_legacy = Creative.objects.get(name='DCM_LEGACY')
        dcm_legacy_ias_monitoring = Creative.objects.get(name='DCM_LEGACY_IAS_MONITORING')
        dcm_legacy_dv_blocking = Creative.objects.get(name='DCM_LEGACY_DV_BLOCKING')
        sizmek_ias_blocking = Creative.objects.get(name='SIZMEK_IAS_BLOCKING')
        sizmek_ias_monitoring = Creative.objects.get(name='SIZMEK_IAS_MONITORING')
        sizmek_dv_blocking = Creative.objects.get(name='SIZMEK_DV_BLOCKING')
        sizmek = Creative.objects.get(name='SIZMEK')
        flashtalking = Creative.objects.get(name='FLASHTALKING')
        flashtalking_ias_blocking = Creative.objects.get(name='FLASHTALKING_IAS_BLOCKING')
        flashtalking_ias_monitoring = Creative.objects.get(name='FLASHTALKING_IAS_MONITORING')

        self.assertEqual(dcm_ins.determine_adserver(), 'dcm ins')
        self.assertEqual(dcm_ins_ias_blocking.determine_adserver(), 'dcm ins')
        self.assertEqual(dcm_ins_ias_monitoring.determine_adserver(), 'dcm ins')
        self.assertEqual(dcm_ins_dv_blocking.determine_adserver(), 'dcm ins')
        self.assertEqual(dcm_legacy.determine_adserver(), 'dcm legacy')
        self.assertEqual(dcm_legacy_ias_monitoring.determine_adserver(), 'dcm legacy')
        self.assertEqual(dcm_legacy_dv_blocking.determine_adserver(), 'dcm legacy')
        self.assertEqual(sizmek_ias_blocking.determine_adserver(), 'sizmek')
        self.assertEqual(sizmek_ias_monitoring.determine_adserver(), 'sizmek')
        self.assertEqual(sizmek_dv_blocking.determine_adserver(), 'sizmek')
        self.assertEqual(sizmek.determine_adserver(), 'sizmek')
        self.assertEqual(flashtalking.determine_adserver(), 'flashtalking')
        self.assertEqual(flashtalking_ias_blocking.determine_adserver(), 'flashtalking')
        self.assertEqual(flashtalking_ias_monitoring.determine_adserver(), 'flashtalking')

    def test_has_blocking(self):
        dcm_ins = Creative.objects.get(name='DCM_INS')
        dcm_ins_ias_blocking = Creative.objects.get(name='DCM_INS_IAS_BLOCKING')
        dcm_ins_ias_monitoring = Creative.objects.get(name='DCM_INS_IAS_MONITORING')
        dcm_ins_dv_blocking = Creative.objects.get(name='DCM_INS_DV_BLOCKING')
        dcm_legacy = Creative.objects.get(name='DCM_LEGACY')
        dcm_legacy_ias_monitoring = Creative.objects.get(name='DCM_LEGACY_IAS_MONITORING')
        dcm_legacy_dv_blocking = Creative.objects.get(name='DCM_LEGACY_DV_BLOCKING')
        sizmek_ias_blocking = Creative.objects.get(name='SIZMEK_IAS_BLOCKING')
        sizmek_ias_monitoring = Creative.objects.get(name='SIZMEK_IAS_MONITORING')
        sizmek_dv_blocking = Creative.objects.get(name='SIZMEK_DV_BLOCKING')
        sizmek = Creative.objects.get(name='SIZMEK')
        flashtalking = Creative.objects.get(name='FLASHTALKING')
        flashtalking_ias_blocking = Creative.objects.get(name='FLASHTALKING_IAS_BLOCKING')
        flashtalking_ias_monitoring = Creative.objects.get(name='FLASHTALKING_IAS_MONITORING')

        self.assertFalse(dcm_ins.has_blocking())
        self.assertFalse(dcm_legacy.has_blocking())
        self.assertFalse(sizmek.has_blocking())
        self.assertFalse(flashtalking.has_blocking())

        self.assertTrue(dcm_ins_ias_blocking.has_blocking())
        self.assertTrue(dcm_ins_ias_monitoring.has_blocking())
        self.assertTrue(dcm_ins_dv_blocking.has_blocking())
        self.assertTrue(dcm_legacy_ias_monitoring.has_blocking())
        self.assertTrue(dcm_legacy_dv_blocking.has_blocking())
        self.assertTrue(sizmek_ias_blocking.has_blocking())
        self.assertTrue(sizmek_ias_monitoring.has_blocking())
        self.assertTrue(sizmek_dv_blocking.has_blocking())
        self.assertTrue(flashtalking_ias_blocking.has_blocking())
        self.assertTrue(flashtalking_ias_monitoring.has_blocking())

    def test_remove_blocking(self):

        dcm_ins_ias_blocking = Creative.objects.get(name='DCM_INS_IAS_BLOCKING')
        dcm_ins_ias_blocking.adserver = 'dcm ins'
        dcm_ins_ias_blocking.blocking_vendor = 'ias'
        dcm_ins_ias_blocking.save()

        dcm_ins_ias_monitoring = Creative.objects.get(name='DCM_INS_IAS_MONITORING')
        dcm_ins_ias_monitoring.adserver = 'dcm ins'
        dcm_ins_ias_monitoring.blocking_vendor = 'ias'
        dcm_ins_ias_monitoring.save()

        dcm_ins_dv_blocking = Creative.objects.get(name='DCM_INS_DV_BLOCKING')
        dcm_ins_dv_blocking.adserver = 'dcm ins'
        dcm_ins_dv_blocking.blocking_vendor = 'dv'
        dcm_ins_dv_blocking.save()

        dcm_legacy_ias_monitoring = Creative.objects.get(name='DCM_LEGACY_IAS_MONITORING')
        dcm_legacy_ias_monitoring.adserver = 'dcm legacy'
        dcm_legacy_ias_monitoring.blocking_vendor = 'ias'
        dcm_legacy_ias_monitoring.save()

        dcm_legacy_dv_blocking = Creative.objects.get(name='DCM_LEGACY_DV_BLOCKING')
        dcm_legacy_dv_blocking.adserver = 'dcm legacy'
        dcm_legacy_dv_blocking.blocking_vendor = 'dv'
        dcm_legacy_dv_blocking.save()

        sizmek_ias_blocking = Creative.objects.get(name='SIZMEK_IAS_BLOCKING')
        sizmek_ias_blocking.adserver = 'sizmek'
        sizmek_ias_blocking.blocking_vendor = 'ias'
        sizmek_ias_blocking.save()

        sizmek_ias_monitoring = Creative.objects.get(name='SIZMEK_IAS_MONITORING')
        sizmek_ias_monitoring.adserver = 'sizmek'
        sizmek_ias_monitoring.blocking_vendor = 'ias'
        sizmek_ias_monitoring.save()

        sizmek_dv_blocking = Creative.objects.get(name='SIZMEK_DV_BLOCKING')
        sizmek_dv_blocking.adserver = 'sizmek'
        sizmek_dv_blocking.blocking_vendor = 'dv'
        sizmek_dv_blocking.save()

        flashtalking_ias_blocking = Creative.objects.get(name='FLASHTALKING_IAS_BLOCKING')

        flashtalking_ias_monitoring = Creative.objects.get(name='FLASHTALKING_IAS_MONITORING')
        flashtalking_ias_monitoring.adserver = 'flashtalking'
        flashtalking_ias_monitoring.blocking_vendor = 'ias'
        flashtalking_ias_monitoring.save()

        self.assertNotIn('pixel.adsafeprotected', dcm_ins_ias_monitoring.remove_blocking())
        self.assertNotIn('pixel.adsafeprotected', dcm_legacy_ias_monitoring.remove_blocking())
        self.assertNotIn('pixel.adsafeprotected', sizmek_ias_monitoring.remove_blocking())
        self.assertNotIn('pixel.adsafeprotected', flashtalking_ias_monitoring.remove_blocking())

        self.assertHTMLEqual(dcm_ins_ias_blocking.remove_blocking(),
                         '''
                         <ins class='dcmads' style='display:inline-block;width:160px;height:600px'
                            data-dcm-placement='N4427.1172840.ADTHEORENTINC/B23519098.267458228'
                            data-dcm-rendering-mode='script'
                            data-dcm-https-only
                            data-dcm-resettable-device-id=''
                            data-dcm-app-id=''>
                          <script src='https://www.googletagservices.com/dcm/dcmads.js'></script>
                        </ins>
                         ''')
        # self.assertTrue(flashtalking_ias_blocking.remove_blocking())
        self.assertHTMLEqual(sizmek_ias_blocking.remove_blocking(),
                             '''
                             <script src="https://bs.serving-sys.com/Serving/adServer.bs?c=28&cn=display&pli=1075099860&w=300&h=600&ord=[timestamp]&z=0"></script>
                             <noscript>
                             <a href="https://bs.serving-sys.com/Serving/adServer.bs?cn=brd&pli=1075099860&Page=&Pos=1474389399" target="_blank">
                             <img src="https://fw.adsafeprotected.com/rfw/bs.serving-sys.com/361042/46613317/Serving/adServer.bs?c=8&cn=display&pli=1075099860&Page=&Pos=1474389399" border=0 width=300 height=600></a>
                             </noscript>
                             ''')

        self.assertHTMLEqual(dcm_legacy_dv_blocking.remove_blocking(),
                             '''
                             <SCRIPT language='JavaScript1.1' SRC="https://ad.doubleclick.net/ddm/adj/N3926.1172840.ADTHEORENTINC/B23165039.254807933;sz=300x250;ord=[timestamp];dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=?">
                             </SCRIPT>
                             '''
                             )
        self.assertHTMLEqual(sizmek_dv_blocking.remove_blocking(),
                             '''
                             <script src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=rsb&c=28&pli=28887076&PluID=0&w=300&h=250&ucm=true&ncu=$$[ENCODEDCLICKURL]/images/invisible.gif$$&ord=[timestamp]&ucm=true"></scr+ipt><noscript><a href="[CLICKURL]https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=brd&FlightID=28887076&Page=&PluID=0&Pos=1120116384" target="_blank"><img src="https://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=bsr&FlightID=28887076&Page=&PluID=0&Pos=1120116384" border=0 width=300 height=250></a></noscript>
                             </script>
                             ''')
        self.assertTrue(dcm_ins_dv_blocking.remove_blocking(),
                        '''
                        <ins class='dcmads' style='display:inline-block;width:728px;height:90px'
                            data-dcm-placement='N30602.1172840ADTHEORENTINC1/B23952138.275863207'
                            data-dcm-rendering-mode='script'
                            data-dcm-https-only
                            data-dcm-resettable-device-id=''
                            data-dcm-app-id=''>
                          <script src='https://www.googletagservices.com/dcm/dcmads.js'></scr+ipt>
                        </ins>
                        </script>
                        ''')

