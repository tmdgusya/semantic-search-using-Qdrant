import os
import uuid
from typing import List
from src.embedd.EmbeddedModel import EmbeddedModel
from src.storage.QueryResultModel import QueryResultModel
from src.storage.StorageInterface import StorageInterface
from src.embedd.EmbeddingInteface import EmbeddingInterface
from src.embedd.openai.OpenAIClient import OpenAIClient

from qdrant_client import QdrantClient
from qdrant_client import models

class QdrantClientStorage(StorageInterface):
    
    def __init__(self, embedding_client: EmbeddingInterface) -> None:
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME")
        self.qdrant_client = QdrantClient(
            host=os.getenv("QDRANT_HOST"), 
            port=os.getenv("QDRANT_PORT"),
        )
        
        if (os.getenv("QDRANT_COLLECTION_ALWAYS_REFRES")):
            print("QDRANT_COLLECTION_ALWAYS_REFRES is set. So, collection will be refreshed.")
            self.qdrant_client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=embedding_client.get_vector_size(), distance=models.Distance.COSINE),
            )
        else:
            print("QDRANT_COLLECTION_ALWAYS_REFRES is not set. So, collection will not be refreshed.")
            if (self.qdrant_client.get_collection(collection_name=self.collection_name) == None):
                print("Collection does not exist. So, collection will be created.")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=embedding_client.get_vector_size(), distance=models.Distance.COSINE),
                )
        
        self.model = embedding_client
    
    def convert_single_data_to_point_struct(self, data: EmbeddedModel) -> models.PointStruct:
        return models.PointStruct(
            id=uuid.uuid4().hex,
            payload={
                "original_text": data.original_text,
                "ref": data.ref,
            },
            vector=data.embedded_text
        )
        
    def convert_data_to_point_structs(self, datas: List[EmbeddedModel]) -> List[models.PointStruct]:
        return [self.convert_single_data_to_point_struct(data) for data in datas]
    
    def save(self, data: EmbeddedModel) -> bool:
        datas = self.convert_data_to_point_structs([data])
        
        result = self.qdrant_client.upsert(
            collection_name=self.collection_name, points=datas
        )
        
        print(result)
        

        return result
    
    def query(self, query: str) -> QueryResultModel:
        # Convert text query into vector
        vector = self.model.embed_simple_text(query)

        # Use `vector` for search for closest vectors in the collection
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=None,  # If you don't want any filters for now
        )
        
        print("Search result: ", search_result)
        # `search_result` contains found vector ids with similarity scores along with the stored payload
        # In this function you are interested in payload only
        payloads = [hit.payload for hit in search_result]
        
        print(f"Payloads: {payloads}")
        return payloads
    

if __name__ == "__main__":
    client = QdrantClientStorage(
        embedding_client=OpenAIClient()
    )
    
    result = client.save(
        data=EmbeddedModel(
            embedded_text=[0.0015061837621033192, 0.0034185831900686026, -0.012801367789506912, -0.03333835303783417, -0.009449690580368042, 0.00477263517677784, -0.015369287692010403, 0.0016710595227777958, -0.00296298461034894, -0.0249782782047987, 0.029922956600785255, 0.007123906631022692, -0.016822105273604393, -0.018007298931479454, 0.010405492037534714, -0.0028004981577396393, 0.02519492618739605, -0.015139894559979439, 0.011272084899246693, 0.01073046401143074, -0.00816254410892725, -0.001796906697563827, 0.017115218564867973, 0.006072525400668383, -0.014247813262045383, -0.007346927188336849, 0.003482303349301219, -0.015930024906992912, 0.037161558866500854, -0.025806639343500137, 0.009902102872729301, -0.006690610200166702, -0.004791751503944397, -0.01386549323797226, 0.011769101954996586, -0.018963100388646126, 0.0050052134320139885, -0.011335805058479309, 0.01901407726109028, -0.011781846173107624, 0.004823611117899418, 0.005607368424534798, 0.0030346696730703115, -0.006270057521760464, -0.026813415810465813, 0.008334588259458542, 0.005448068492114544, -0.009233041666448116, -0.006117129232734442, 0.020517870783805847, 0.02041591890156269, -0.011807333678007126, -0.013648844324052334, 0.007671899627894163, -0.01856803707778454, -0.00045878469245508313, -0.038359496742486954, 0.023971499875187874, 0.030916990712285042, -0.022161848843097687, 0.01974048651754856, 0.008028732612729073, -0.022939234972000122, 0.010035915300250053, -0.010341771878302097, 0.005132653750479221, 0.014260557480156422, 0.013954700902104378, -0.02227654494345188, 0.024111684411764145, 0.020097319036722183, 0.001941869966685772, -0.0056487866677343845, -0.0048140534199774265, 0.020161038264632225, 0.00029331157566048205, -0.02050512656569481, 0.005916411057114601, 0.00041497714119032025, -0.008742397651076317, 0.02869953215122223, -0.035963620990514755, -0.013253780081868172, 0.014630134217441082, 0.02228928916156292, 0.003644789569079876, -0.005855876952409744, 0.022748075425624847, -0.016936801373958588, -0.015356543473899364, -0.009889358654618263, 0.005846318788826466, 0.015522215515375137, 0.013852749019861221, -0.024047965183854103, 0.01289694756269455, 0.002927938476204872, 0.03106991946697235, -0.0002837535575963557, -0.035963620990514755, -0.013241035863757133, -0.0037276255898177624, -0.010354516096413136, -0.014107629656791687, -0.019434629008173943, 0.0072067431174218655, -0.011049064807593822, -0.0020294850692152977, 0.027476105839014053, 0.0013524590758606791, -0.023270579054951668, 0.00890806969255209, -0.0004918394843116403, -0.03323640301823616, -0.0026491631288081408, -0.008468400686979294, -0.0009215518948622048, 0.010647628456354141, 0.0013293605297803879, -0.02033945545554161, 0.01864450052380562, 0.021257024258375168, 0.0064771478064358234, -0.023385275155305862, 0.0021441811695694923, 0.004094016272574663, -0.034612756222486496, -0.021601112559437752, -0.0077292476780712605, -0.012508255429565907, 0.025309622287750244, -0.001983287977054715, -0.004125876352190971, 0.00026045588310807943, -0.033363841474056244, 0.02734866552054882, -0.011240225285291672, 0.01944737322628498, -0.02198343351483345, -0.009392342530190945, 0.000893674383405596, 0.027934890240430832, 0.011864681728184223, -0.001941869966685772, -0.007066558580845594, 0.020772751420736313, 0.0040175518952310085, -0.013610612601041794, 0.013355731964111328, -0.0068753985688090324, 0.005709320772439241, 0.018542548641562462, 0.011017204262316227, 0.0038359498139470816, 0.012412674725055695, 0.03489312529563904, -0.0016885825898498297, 0.020747262984514236, 0.004326594527810812, -0.0173573549836874, 0.0037021376192569733, -0.008729653432965279, 0.0065026357769966125, -0.025437062606215477, 0.01744656264781952, 0.01909054070711136, 0.01989341340959072, 0.011010833084583282, -0.00995307881385088, -0.020237503573298454, -0.012081330642104149, 0.003178039798513055, -0.04294734448194504, 0.02281179465353489, -0.01464287843555212, 0.015343799255788326, 0.004014366306364536, 0.01610844023525715, -0.014349766075611115, -0.0294386837631464, -0.02765452116727829, 0.008850721642374992, 0.003533279290422797, 0.029719052836298943, 0.009188437834382057, 8.258721936726943e-05, 0.012922435998916626, -0.011495104990899563, 0.0049000754952430725, -0.013890980742871761, 0.008697792887687683, 0.03764583170413971, 0.024430284276604652, 0.017395585775375366, -0.6867496967315674, -0.01188379805535078, 0.019421884790062904, 0.018797429278492928, 0.00616810517385602, 0.00987024325877428, 0.007684643846005201, 0.03731448948383331, 0.00032815849408507347, 0.029489660635590553, -0.02093842439353466, 0.022760817781090736, -0.014222325757145882, -0.0067224702797830105, -0.007353299297392368, -0.014808550477027893, 0.004046225920319557, -0.015483983792364597, -0.0049383076839149, 0.007009210530668497, -0.01285234373062849, 0.029030876234173775, -0.023601923137903214, -0.01684759370982647, 0.011756357736885548, 0.00872328132390976, 0.006400683894753456, -0.015420263633131981, -0.014489949680864811, 0.0323188342154026, -0.00395064614713192, 0.0131135955452919, 0.00553409056738019, 0.006203151308000088, 0.04970167577266693, 0.015840815380215645, 0.0021569253876805305, 0.001507776789367199, 0.007971384562551975, 0.02974454127252102, -0.019995367154479027, -0.019778717309236526, 0.010622140020132065, -0.016452528536319733, 0.008857093751430511, 0.004998841788619757, 0.003101575654000044, -0.00577941257506609, 0.0038964839186519384, 0.007123906631022692, 0.01640155352652073, -0.0007168510928750038, 0.014859526418149471, 0.018886636942625046, -0.000741542608011514, 0.007761107757687569, 0.01578984037041664, 0.014528182335197926, -5.650180537486449e-05, 0.005400278139859438, 0.0014329056721180677, 0.02109135128557682, -0.0018032786902040243, 0.006072525400668383, -0.019358165562152863, 0.01856803707778454, -0.01818571612238884, 0.01491050235927105, -0.0038805538788437843, -0.012164166197180748, -0.012495511211454868, -0.0067415861412882805, -0.014935990795493126, -0.01840236410498619, 0.0063720098696649075, 0.025819383561611176, 0.02570468746125698, -0.0034472572151571512, -0.005263280123472214, 0.017497537657618523, 0.017306378111243248, 0.017178937792778015, -0.006544054020196199, -0.023359786719083786, 0.016567224636673927, -0.023130394518375397, -0.031044431030750275, -0.017867114394903183, 0.0019801019225269556, 0.004444476682692766, 0.037085097283124924, 0.007079302798956633, -0.010335399769246578, -0.029795518144965172, 0.02429010160267353, 0.006279615685343742, -0.012622951529920101, -0.00197532307356596, 0.017548514530062675, -0.00890806969255209, 0.010176099836826324, 0.0006256516790017486, 0.007907664403319359, -0.0011302352650091052, 0.01618490368127823, 0.012508255429565907, -0.001260064891539514, 0.04167294502258301, 0.021409953013062477, -0.02547529526054859, -0.005174071993678808, 0.005655158776789904, -0.0374419279396534, 0.01505068689584732, 0.01170538179576397, -0.024646934121847153, 0.001405028160661459, 0.022034408524632454, 0.029897470027208328, -0.014668365940451622, 0.022862771525979042, -0.00853849295526743, 0.009647222235798836, 0.007869431748986244, 0.0026013730093836784, 0.015343799255788326, -0.01345768477767706, 0.006330591626465321, -0.016286857426166534, 0.005479928106069565, 0.01826217956840992, 0.007378787267953157, 0.0011477582156658173, -0.0034791172947734594, 0.004947865381836891, 0.007143022958189249, 0.015458495356142521, -0.011323060840368271, 0.0032847709953784943, 0.02086195908486843, -0.008009616285562515, 0.0035046052653342485, 0.0004094016330782324, -0.0016726525500416756, 0.009621734730899334, -0.01907779648900032, -0.0017602676525712013, 0.01781613938510418, 0.005683832801878452, -0.006098013371229172, 0.014413486234843731, -0.008933557197451591, -0.028113307431340218, 0.02847013995051384, -0.011374037712812424, -0.0023719805758446455, -0.007550831418484449, -0.025806639343500137, -0.026252679526805878, -0.031018942594528198, 0.010233447887003422, 0.017382841557264328, -0.011151016689836979, 0.003982506226748228, -0.011730870231986046, -0.027297688648104668, -0.020619822666049004, 0.02304118685424328, 0.0046356371603906155, -0.022837283089756966, 0.005352488253265619, -0.011412269435822964, -0.024239124730229378, -0.0038869259878993034, -0.0027144760824739933, 0.010947112925350666, -0.012387187220156193, -0.022544169798493385, -0.0011605023173615336, -0.020390430465340614, 0.004450848791748285, -0.007990499958395958, -0.002359236590564251, 0.017918091267347336, 0.02691536955535412, -0.002802091185003519, 0.002314632525667548, 0.022939234972000122, -0.024646934121847153, -0.010832416824996471, 0.017268145456910133, 0.011947518214583397, -0.019205236807465553, -0.004594218917191029, 0.002136216266080737, -0.01824943535029888, -0.0026427910197526217, -0.0017682326724752784, 0.008787001483142376, 0.019613046199083328, 0.020658055320382118, 0.007761107757687569, 0.020301222801208496, -0.02602328732609749, -0.01981694996356964, -0.026966344565153122, -0.0008442912949249148, -0.031095407903194427, 0.005473556462675333, 0.016363320872187614, 0.011437756940722466, 0.001302279531955719, -0.0003339331306051463, 0.016439784318208694, 0.018071020022034645, 0.02408619597554207, -0.0013309535570442677, -0.022391242906451225, -0.022684354335069656, 0.00596101488918066, 0.0036670914851129055, 0.01427330169826746, -0.016146672889590263, -0.006773446220904589, 0.00853849295526743, 0.031426750123500824, 0.008232636377215385, 0.04024561494588852, 0.010634884238243103, -0.026940856128931046, -0.019268957898020744, 0.01773967407643795, 0.011820077896118164, 0.014349766075611115, -0.008054220117628574, -0.0025010136887431145, 0.001906823948957026, -0.013024387881159782, 0.03524995595216751, 0.0127057870849967, -0.007461623288691044, 0.013585124164819717, 0.0266095120459795, -0.017472051084041595, -0.0032130859326571226, 0.029973933473229408, 0.02064531110227108, -0.0065886578522622585, 0.003115912666544318, 0.028419163078069687, -0.01069860439747572, -0.004450848791748285, -0.0013269709888845682, -0.014528182335197926, 0.01468111015856266, -0.030866015702486038, 0.008602213114500046, -0.015114407055079937, 0.021193305030465126, 0.032752130180597305, 0.02079823985695839, 0.008621329441666603, 0.003415397135540843, -0.00652175210416317, 0.00419596815481782, -0.012763135135173798, -0.005479928106069565, -0.013954700902104378, 0.005244163796305656, -0.0009661559597589076, -0.02227654494345188, -0.01147598959505558, 0.027603546157479286, -0.03777327388525009, 0.0059737591072916985, 0.00316688884049654, -0.0046356371603906155, -0.010284423828125, -0.007391531020402908, 0.0005495858495123684, -0.0083537045866251, -0.02676244080066681, 0.0013245815644040704, 0.006582286208868027, 0.004829983226954937, -0.012839599512517452, -0.029795518144965172, -0.00954527035355568, -0.00557232229039073, -0.003638417460024357, -0.0001859830372268334, 0.008978161960840225, 0.0073596709407866, -0.02630365639925003, 0.011896542273461819, -0.003737183753401041, 0.025666454806923866, 0.0030282975640147924, -0.0015037943376228213, -0.015968255698680878, 0.014783062040805817, 0.022709842771291733, -0.006524937693029642, -0.018274923786520958, 0.005358860362321138, 0.0001771219540387392, -0.006639634259045124, -0.02228928916156292, 0.007085674908012152, -0.015420263633131981, 0.0061712912283837795, 0.002818021224811673, -0.0007514989119954407, 0.004039854276925325, 0.010571164079010487, 0.0012106818612664938, -0.0009573944262228906, 0.023793084546923637, 0.02974454127252102, 0.0063242195174098015, 0.006684238091111183, -0.0013755576219409704, -0.021792273968458176, -0.008506633341312408, 0.07620923221111298, 0.000902435858733952, 0.002529687946662307, 0.016197647899389267, -0.015891792252659798, -0.0086786774918437, -0.026176216080784798, -0.021664833649992943, -0.02109135128557682, -0.011151016689836979, -0.0012584718642756343, 0.002308260416612029, -0.017637722194194794, 0.008143428713083267, 0.008047848008573055, 0.008213520050048828, 0.004489080980420113, -0.015458495356142521, -0.0077101318165659904, 0.009825638495385647, -0.009003649465739727, 0.009513410739600658, -0.002639604965224862, 0.01087702065706253, 0.024876326322555542, 0.0008251752587966621, 0.006862654350697994, 0.012680299580097198, -0.008200776763260365, -0.009832010604441166, 0.00458466075360775, -0.009679082781076431, 0.018529804423451424, 0.0019179749069735408, 0.013546892441809177, 0.014362509362399578, -0.009194809943437576, 0.029183804988861084, 0.010558419860899448, -0.010947112925350666, 0.006690610200166702, 0.0032911431044340134, -0.009035510011017323, -0.0029438685160130262, 0.01013149507343769, 0.0023066673893481493, -0.008959045633673668, 0.02796037867665291, -0.002451630774885416, -0.02719573676586151, 0.02205989696085453, 0.0015969849191606045, -0.00815617199987173, -0.014337021857500076, -0.014005676843225956, 0.01566240005195141, 0.0038741817697882652, -0.016006488353013992, -0.014744830317795277, -0.017828883603215218, -0.0070920465514063835, -0.018440596759319305, -0.016681920737028122, -0.009430574253201485, -0.022110873833298683, -0.026660488918423653, -0.02265886589884758, -0.004903261549770832, -0.011488733813166618, -0.005798528902232647, -0.010622140020132065, -0.04521578177809715, -0.016452528536319733, -0.004062156192958355, 0.019268957898020744, 0.0019100098870694637, 0.005884550977498293, -0.006107571069151163, 0.0051422119140625, 0.0020740891341120005, -0.014222325757145882, -0.02706829644739628, 0.01303713209927082, -0.01073683612048626, 0.014426229521632195, 0.004007994197309017, -0.0042565022595226765, 0.00946243479847908, -0.022008921951055527, 0.03122284822165966, 0.00207727518863976, 0.024175405502319336, 0.022161848843097687, 0.001949834986589849, 0.007659155409783125, 0.007665527518838644, -0.000774995656684041, -0.0011111191706731915, -0.018211204558610916, -0.0005583473248407245, -0.005540462210774422, -0.008627701550722122, -0.001166874310001731, -0.010335399769246578, -0.00024372937332373112, 0.008857093751430511, 0.010902508161962032, 0.024111684411764145, -0.016197647899389267, 4.126871863263659e-05, 0.03489312529563904, -0.02295197919011116, 0.018134739249944687, 0.0022971094585955143, 0.002666685963049531, 0.007334182970225811, 0.02765452116727829, 0.0314522385597229, 0.0005483910790644586, -0.032242368906736374, -0.0022190522868186235, -0.0225824024528265, 0.006582286208868027, 0.01524184737354517, 0.006381567567586899, -0.00037455468554981053, -0.0023225974291563034, -0.015636911615729332, -0.011055436916649342, -0.0007522953674197197, -0.006432543974369764, 0.016528993844985962, -0.0025567689444869757, -0.006760702468454838, -0.00557232229039073, -0.008398308418691158, -0.02056884765625, 0.010806928388774395, -0.004211898427456617, -0.015687888488173485, -0.017421074211597443, -0.00637519545853138, -0.0022015294525772333, -0.014222325757145882, -0.04399235546588898, -0.04264148697257042, -0.007448879536241293, -0.0024054336827248335, -0.007684643846005201, 0.01856803707778454, -0.002743150107562542, 0.0008912848425097764, -0.019065052270889282, -0.014120373874902725, -0.0014161791186779737, -0.020288478583097458, -0.003600185504183173, -0.003753113793209195, 0.026940856128931046, 0.025284133851528168, 0.023385275155305862, 0.014744830317795277, 0.01638880930840969, 0.0006180849159136415, -0.0007391531253233552, -0.009736430831253529, 0.00936048198491335, -0.004970167763531208, -0.012170538306236267, 0.007678271736949682, 0.017765162512660027, 0.018198460340499878, -0.013572380878031254, 0.017089730128645897, 0.0013213955098763108, -0.008047848008573055, -0.015496727079153061, 0.01069860439747572, -0.01767595484852791, -0.017561258748173714, -0.02824074774980545, -0.0018016857793554664, 0.003976134117692709, 0.004122690297663212, 0.0039060418494045734, -0.011730870231986046, 0.016274113208055496, 0.012278862297534943, 0.019511094316840172, 0.0038741817697882652, 0.033797141164541245, -0.024787116795778275, 0.024417541921138763, 0.008876209147274494, 0.012992527335882187, -0.017102474346756935, -0.0026284540072083473, -0.012164166197180748, 0.022990209981799126, 0.004368012771010399, 0.017981810495257378, 0.023283323273062706, -0.006798934191465378, -0.009264902211725712, 0.0015149452956393361, 0.027527082711458206, -0.00573799479752779, 0.002829172182828188, 0.005868620704859495, -0.006088455207645893, 0.002034264151006937, -0.021142328158020973, -0.00036220892798155546, -0.013572380878031254, 0.004281990695744753, -0.01578984037041664, -0.019116029143333435, 0.011947518214583397, -0.017472051084041595, -0.03481665998697281, -0.019804205745458603, 0.0008570352802053094, 0.045725543051958084, -0.004020737949758768, 0.00936048198491335, 0.022646121680736542, 0.0025089788250625134, 0.0012393558863550425, 0.011170133017003536, -0.01675838604569435, -0.004317036364227533, 0.038130104541778564, 0.007984127849340439, -0.010794184170663357, -0.013139083981513977, -0.0004460406780708581, 0.00556913623586297, -0.013470428064465523, -0.01826217956840992, -0.0007961029768921435, 0.023359786719083786, 0.002255691448226571, -0.01617216132581234, 0.006212709471583366, -0.02824074774980545, 0.021677576005458832, -0.002214273437857628, -0.021193305030465126, -0.02005908638238907, 0.007302322890609503, -0.023372530937194824, 0.0163250882178545, -0.02033945545554161, 0.03323640301823616, 0.02304118685424328, -0.014859526418149471, -0.0064771478064358234, 0.004100388381630182, 0.0008152190130203962, -0.009812895208597183, -0.000826768227852881, 0.025360599160194397, -0.0035269074141979218, 0.0004623689455911517, 0.013030759990215302, -0.0017220355803146958, -0.0167074091732502, -0.008137056604027748, -0.0070538148283958435, 0.023793084546923637, -0.02370387688279152, 0.007429763209074736, -0.005451254080981016, 0.009309506043791771, 0.00020131567725911736, 0.014362509362399578, -0.014744830317795277, -0.015675144270062447, 0.0033930952195078135, -0.00064755545463413, 0.03280310705304146, 0.0027734171599149704, 0.0009565979707986116, -0.018083764240145683, -0.013164572417736053, -0.027170248329639435, -0.0512564443051815, -0.0005344523233361542, -0.005492672324180603, -0.0335167720913887, -0.013699821196496487, -0.003883739933371544, 0.009475178085267544, 0.018657244741916656, 0.01787985861301422, -0.009965823031961918, 0.013572380878031254, 0.02369113266468048, -0.016044721007347107, -0.005591438617557287, 0.02683890424668789, 0.014795806258916855, -0.028342699632048607, 0.01840236410498619, -0.003329375060275197, -0.020454151555895805, 0.0013317500706762075, -0.00811794027686119, -0.010596652515232563, 0.0069136302918195724, 0.01166077796369791, 0.008812488988041878, -0.009991311468183994, 0.008417424745857716, 0.029234779998660088, 0.028648555278778076, 0.018669988960027695, -0.00754445930942893, -0.010176099836826324, 0.04779007285833359, -0.009456062689423561, -8.965616871137172e-05, -0.0047280313447117805, -0.012412674725055695, 0.02407345175743103, -0.007493483368307352, -0.016376065090298653, 0.007996872067451477, -0.037365466356277466, -0.004998841788619757, -0.005795342847704887, -0.006301917601376772, 0.009698199108242989, -0.025092974305152893, -0.02256965823471546, -0.007015582639724016, -0.017905347049236298, 0.002376759657636285, 0.008442913182079792, -0.016414297744631767, -0.0030171466059982777, 0.0171407051384449, 0.01893761195242405, -0.004199154209345579, -0.0006443694583140314, -0.011361293494701385, -0.0175230260938406, -0.014617389999330044, -0.02212361805140972, -0.014885014854371548, -0.004027110058814287, 0.04159647971391678, 0.012368070892989635, -0.011214736849069595, -0.00987024325877428, 0.0020804612431675196, -0.026660488918423653, -0.033363841474056244, -0.0016853965353220701, -0.005871806759387255, 0.0017411516746506095, 0.012986156158149242, -0.002861032262444496, 0.012272490188479424, 0.004657939076423645, 0.000997219467535615, -0.013368476182222366, -0.016745641827583313, 0.021346231922507286, -0.0031971558928489685, 0.01767595484852791, 0.005362045951187611, -0.030152350664138794, -0.001881335861980915, 0.0019769161008298397, 0.014553669840097427, -0.011501477099955082, 0.012552859261631966, -0.004626078996807337, -0.012399930506944656, -0.011004460975527763, -0.010679488070309162, 0.00015133523265831172, 0.008965417742729187, 0.021805016323924065, -0.012845971621572971, -0.004992469679564238, 0.00042652638512663543, -0.0074233911000192165, 0.005588252563029528, -0.009328622370958328, 0.014413486234843731, -0.018211204558610916, 0.013202804140746593, -0.021601112559437752, -0.005221861880272627, -0.007193998899310827, -0.01678387261927128, 0.00693274661898613, -0.017841627821326256, 0.007920407690107822, 0.024481261149048805, 0.0008873023325577378, 0.00912471767514944, -0.004629265051335096, 0.0002491057675797492, -0.006544054020196199, 0.00932225026190281, 0.00016049499390646815, -0.013151828199625015, 0.002727220067754388, 0.0034600012004375458, -0.018669988960027695, -0.025526270270347595, 0.005355674307793379, -0.03609106317162514, -0.009003649465739727, -0.0065886578522622585, 0.0338481143116951, 0.015840815380215645, -0.020364942029118538, -0.008589468896389008, -0.019778717309236526, 0.00012465243344195187, 0.010564791969954967, -0.017994554713368416, 0.0077292476780712605, -0.007633667439222336, 0.006177663337439299, 0.02525864541530609, -0.016286857426166534, 0.002666685963049531, 0.01759949140250683, 0.013393964618444443, -0.006311475764960051, 0.02691536955535412, 0.2322470098733902, -0.011679893359541893, 0.010443723760545254, 0.02436656504869461, 0.013648844324052334, 0.017178937792778015, 0.010615767911076546, -0.0009215518948622048, 0.001506980275735259, 0.01423506997525692, -0.009405085816979408, -0.00476944912225008, -0.0008411052986048162, 0.0075380876660346985, 0.002367201494053006, 0.0015284857945516706, -0.018338643014431, -0.015522215515375137, -0.029158316552639008, -0.02773098647594452, -0.004855471197515726, -0.030203325673937798, -0.019651276990771294, -0.017905347049236298, 0.017344610765576363, -0.009366854093968868, -0.006805306300520897, 0.0028928923420608044, 0.03328737989068031, 0.0061330595053732395, -0.006970978807657957, -0.01483403891324997, 0.010787812061607838, 0.006607774179428816, -0.006939118728041649, -0.023907780647277832, 0.032242368906736374, 0.005604182370007038, 0.03756937012076378, 0.007461623288691044, -0.010195215232670307, -0.01677113026380539, -0.005059375893324614, -0.0147193418815732, 0.01110641285777092, 0.009634478949010372, 0.002249319339171052, -0.0262271910905838, 0.008417424745857716, 0.03448531776666641, 0.0006324219866655767, 0.009558014571666718, 0.012603835202753544, 0.03369518741965294, 0.0004894500016234815, -0.013980189338326454, 0.011775474064052105, 0.013572380878031254, 0.0019769161008298397, -0.003848693799227476, 5.092629726277664e-05, 0.02796037867665291, -0.0041513643227517605, 0.027985867112874985, -0.022008921951055527, 0.007512599229812622, -0.030738575384020805, -0.0009048253996297717, 0.008340960368514061, -0.009819267317652702, -0.015343799255788326, -0.004887331277132034, 0.013190059922635555, -0.0059737591072916985, -0.028979899361729622, -0.0038518798537552357, 0.014515438117086887, -0.004313850775361061, 0.025322366505861282, 0.01780339516699314, -0.0029836934991180897, 0.005632856395095587, -0.005699762608855963, -0.018886636942625046, -0.03214041516184807, -0.02877599559724331, 0.005008399486541748, -0.002819614252075553, -0.015509471297264099, -0.023665644228458405, -0.009583503007888794, -0.01152059342712164, -0.00011698611342580989, -0.0019307188922539353, 0.026787929236888885, 0.02392052486538887, -0.0021425881423056126, 0.014362509362399578, -0.01367433276027441, 0.008289984427392483, -0.007327811326831579, 0.002682616002857685, -0.0054034641943871975, 0.01285871583968401, -0.0043297805823385715, 0.0027973123360425234, -0.009647222235798836, 2.237048420283827e-06, -0.0009940335294231772, -0.0237803403288126, -0.029617100954055786, -0.0067224702797830105, 0.004371198825538158, -0.0017411516746506095, -0.008780629374086857, 0.0018542548641562462, -0.00032835762249305844, 0.005744366906583309, -0.0051390258595347404, -0.011941146105527878, -0.0023624226450920105, -0.012215142138302326, -0.013521404936909676, -0.00019444586359895766, -0.004845913499593735, -0.02183050476014614, -0.007015582639724016, -0.003893297864124179, 0.013597868382930756, -0.029387708753347397, 0.015904536470770836, -0.0010927997063845396, 0.027705498039722443, 0.014247813262045383, -0.006945490371435881, 0.010978972539305687, 0.014158605597913265, -0.00592596922069788, -0.015993744134902954, -0.0010235040681436658, 0.002794126281514764, -0.022340266034007072, 0.016286857426166534, -0.006703353952616453, -0.01427330169826746, -0.01091525238007307, 0.03496959060430527, -0.026558537036180496, -0.00010483946971362457, 0.006658750120550394, -0.03524995595216751, -0.011934773996472359, -0.008455656468868256, -0.0114823617041111, 0.026813415810465813, -0.017013266682624817, -0.022671610116958618, -0.026584023609757423, -0.0022859585005789995, 0.0030346696730703115, -0.026354631409049034, 0.012278862297534943, 0.036193013191223145, -0.0017650467343628407, -0.025908591225743294, -0.013253780081868172, -0.16342930495738983, 0.015496727079153061, 0.01601923257112503, -0.020747262984514236, 0.027170248329639435, 0.010558419860899448, 0.030534669756889343, 0.0027351852040737867, -0.005890923086553812, 0.021142328158020973, 0.008009616285562515, -0.018759196624159813, -0.01427330169826746, -0.007843944244086742, 0.0043042926117777824, -0.009271274320781231, -0.006531309802085161, 0.017714187502861023, 0.03191102296113968, 0.027680009603500366, 0.026584023609757423, -0.019256213679909706, 0.010309911333024502, -0.003139807842671871, 0.011533337645232677, -0.009468805976212025, -0.0038901118095964193, 0.037238024175167084, -0.01691131293773651, -0.007984127849340439, -0.016605457291007042, -0.02281179465353489, 0.022913746535778046, 0.011635289527475834, 0.01743381842970848, 0.00025229176389984787, 0.012756763026118279, -0.04399235546588898, -0.016044721007347107, 0.02004634216427803, 0.02519492618739605, 0.011953890323638916, 0.02384405955672264, -0.016452528536319733, -0.01531831081956625, -0.008360076695680618, 0.020912935957312584, 0.01930718868970871, 0.02467242069542408, -0.009309506043791771, 0.010023171082139015, -0.004759891424328089, 0.003638417460024357, -0.017344610765576363, 0.02765452116727829, 0.028521114960312843, -0.0009096043650060892, 0.017714187502861023, 0.00023018884530756623, -0.004944679327309132, -0.0003016748232766986, -0.01661820150911808, -0.005467184353619814, 0.002614116994664073, 0.01106818113476038, -0.008047848008573055, 0.004664311185479164, 0.013623356819152832, -0.0005651176325045526, 0.012807739898562431, -0.008659561164677143, -0.024532238021492958, -0.011074553243815899, -0.031171871349215508, 0.0046738688834011555, 0.006018362939357758, -0.03369518741965294, 0.018593523651361465, -0.014069397002458572, -0.026252679526805878, -0.009965823031961918, 0.02831721119582653, 0.00012166555825388059, 0.0036989515647292137, -0.018287668004631996, 0.0001601963012944907, 0.004970167763531208, 0.018427852541208267, -0.031018942594528198, -0.040500491857528687, 0.014349766075611115, -0.012495511211454868, -0.007952268235385418, -0.021346231922507286, 0.0004105963744223118, 0.01743381842970848, 0.018236691132187843, 0.010660371743142605, -0.017051497474312782, -0.013151828199625015, 0.002110728295519948, 0.00839193630963564, -0.018517060205340385, 0.013738052919507027, 0.03948097303509712, -0.005196373909711838, 0.007850316353142262, 0.004403058905154467, 0.024685164913535118, -0.026176216080784798, -0.03257371485233307, 0.0070729306899011135, 0.015534959733486176, 0.02706829644739628, 0.01363610103726387, 0.02384405955672264, -0.003141400869935751, -0.017701443284749985, 0.003415397135540843, -0.014808550477027893, 0.05327000096440315, -0.00473121739923954, -0.04330417886376381, 0.0006280412198975682, 0.00308405258692801, -0.010571164079010487, -0.08701616525650024, -0.026278167963027954, -0.0003847100888378918, 0.00950703863054514, 0.006626890040934086, 0.04779007285833359, 0.005795342847704887, 0.005645600613206625, -0.0005627280916087329, 0.00969182699918747, 0.004520941060036421, -0.030075885355472565, -0.024799861013889313, -0.0118901701644063, 0.042233679443597794, -0.03219139203429222, 0.013100852258503437, 0.0011087296297773719, -0.02816428244113922, 0.013967445120215416, -0.005687018856406212, -0.0005587455816566944, 0.0008737618336454034, -0.008137056604027748, -0.017344610765576363, 0.012559231370687485, -0.020734518766403198, 0.030916990712285042, 0.003338932991027832, -0.012132306583225727, -0.021435441449284554, -0.02734866552054882, -0.011839194223284721, -0.008245380595326424, 0.0033739791251719, 0.011832822114229202, -0.04055146872997284, 0.031630657613277435, 0.012693042866885662, -0.04011817276477814, 0.025844871997833252, 0.011692637577652931, -0.006442101672291756, -0.06407693028450012, -0.0039028560277074575, 0.01826217956840992, -0.0017570817144587636, 0.03535190969705582, 0.011654405854642391, -0.010048659518361092, -0.026405608281493187, -0.025322366505861282, -0.026201704517006874, 0.00395064614713192, 0.0185552928596735, -0.006308289710432291, 0.008748768828809261, 0.03078955039381981, 0.0037658577784895897, 0.01106180902570486, 0.011297573335468769, 0.004301106557250023, -0.020084574818611145, 0.015420263633131981, -0.007448879536241293, 0.01824943535029888, -0.015420263633131981, 0.02481260523200035, 0.005776226986199617, 0.00114138622302562, -0.019804205745458603, 0.021728552877902985, 0.007238603197038174, 0.014413486234843731, -0.033210914582014084, -0.00635289354249835, -0.019613046199083328, -0.010481955483555794, 0.010647628456354141, -0.0009056218550540507, -0.0342814102768898, -0.017790650948882103, 0.018083764240145683, -0.0009223484084941447, 0.017459306865930557, 0.010125122964382172, -0.013444940559566021, 0.002598186954855919, -0.008245380595326424, -0.03420494869351387, -0.02839367464184761, 0.002290737582370639, 0.011233853176236153, -0.00653768191114068, 0.010080519132316113, 0.006862654350697994, -0.006387939676642418, -0.00026762441848404706, 0.018580779433250427, 0.012826855294406414, -0.03244627267122269, 0.002904043300077319, -0.0654023066163063, 0.02974454127252102, -0.014222325757145882, -0.03157968074083328, -0.000293709832476452, -0.014783062040805817, 0.008850721642374992, -0.015063431113958359, 0.000749507627915591, -0.012884203344583511, -0.014757574535906315, -0.006225453224033117, 0.009264902211725712, 0.014808550477027893, -0.030916990712285042, 0.005929154809564352, 0.007843944244086742, 0.012597463093698025, 0.009832010604441166, 0.00612668739631772, 0.010564791969954967, -0.035887159407138824, -0.008748768828809261, -0.0049383076839149, -0.024188147857785225, 0.007805712055414915, -0.03346579521894455, -0.002195157343521714, -0.0033102589659392834, -0.010265307500958443, 0.013992933556437492, -0.04123964533209801, 0.009787406772375107, 0.021779529750347137, 0.010080519132316113, -0.008876209147274494, 0.004581475164741278, 0.022556914016604424, -0.0007893326692283154, 0.02451949380338192, -0.02824074774980545, -0.027603546157479286, 0.010290795937180519, -0.016643689945340157, -0.007009210530668497, 0.004320222418755293, -0.0047216592356562614, 0.0013301570434123278, 0.03423043712973595, 0.021409953013062477, -0.009080113843083382, 0.033873602747917175, -0.0318855382502079, -0.015917280688881874, -0.014935990795493126, -0.014056653715670109, -0.005448068492114544, 0.004275618586689234, -0.0025838499423116446, -0.03810461610555649, 0.029260268434882164, 0.006677865982055664, 0.02719573676586151, -0.005983317270874977, 0.006824422162026167, 0.0017156635876744986, -0.023270579054951668, 0.0013859120663255453, -0.017905347049236298, -0.02256965823471546, -0.00973005872219801, -0.012699414975941181, 0.005033887457102537, -0.0015985779464244843, 0.018466083332896233, 0.020632566884160042, -0.0072449748404324055, 0.013126339763402939, -0.04368649795651436, 0.03637143224477768, 0.014387997798621655, 0.016796616837382317, -0.029617100954055786, -0.0015252998564392328, 0.039226092398166656, 0.012597463093698025, -0.008277240209281445, -0.010947112925350666, -0.0015284857945516706, -0.006368823815137148, -0.027858426794409752, -0.017051497474312782, 0.007487111259251833, 0.027323177084326744, 0.0034345132298767567, 0.010577536188066006, 0.021588368341326714, 0.011004460975527763, 0.021269768476486206, 0.023818572983145714, -0.005448068492114544, 0.016681920737028122, -0.020326711237430573, -0.0067479582503438, -0.01640155352652073, 0.010456467978656292, -0.006646005902439356, -0.04044951871037483, 0.007678271736949682, 0.010685860179364681, 0.010724091902375221, 0.03550483658909798, -0.0008681862964294851, 0.011641661636531353, -0.026584023609757423, -0.010195215232670307, 0.024124428629875183, 0.004916005302220583, -0.026048775762319565, 0.04350808262825012, -0.013585124164819717, 0.005699762608855963, 0.022901002317667007, -0.02070903219282627, 0.004227828234434128, -0.000404423481086269, -0.012374443002045155, -0.011405897326767445, 0.012202398851513863, -0.0010824451455846429, 0.018007298931479454, -0.005103979725390673, -0.023130394518375397, -0.0040653422474861145, -3.1685813155490905e-05, 0.02072177454829216, -0.007155766710639, 0.025653710588812828, -0.014158605597913265, 0.052352432161569595, -0.007856687530875206, -0.0017602676525712013, 0.02281179465353489, 0.02199617773294449, 0.013967445120215416, 0.01884840428829193, 0.015573191456496716, -0.009921219199895859, -0.01587904803454876, -0.006422985810786486, 0.010481955483555794, 0.006515379995107651, -0.02773098647594452, -0.025526270270347595, 0.0024643747601658106, -0.021703064441680908, -0.0009645629907026887, -0.015331055037677288, 0.01870821975171566, 0.01878468506038189, 0.013597868382930756, 0.028801484033465385, 0.006117129232734442, -0.024723397567868233, -0.014260557480156422, 0.003354863030835986, 0.00734055507928133, -0.0072449748404324055, -0.023742107674479485, 0.016146672889590263, 0.009194809943437576, -0.010609395802021027, -0.012234258465468884, -5.660136594087817e-05, 0.0027144760824739933, -0.013419452123343945, -0.0038295777048915625, -0.0007789781666360795, 0.005750738549977541, 0.02430284582078457, 0.004638823214918375, -0.025615479797124863, -0.026431096717715263, 0.004106760025024414, 0.005186815746128559, -0.030585646629333496, -0.002537652850151062, -0.01923072524368763],
            original_text="Hello, world!",
            ref="https://www.google.com"
        )
    )
    
    query_result = client.query(
        query="Find Hello",
    )
    
    print(query_result)