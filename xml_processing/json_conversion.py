import join
import os


{

    "Block": [
        {
            "BlockDef": {"BlockName": 'PIC400'}
        },
        {
            "Parameters": {"Parameter":[{"ParamName": 'ABCD', "ParamValue": 0},
                                        {"ParamName": 'EFGC', "ParamValue": 'ON'}]}
        },
        {
            "SymbolAttrs": {"SymbolAttr": [{"ParamName": 'PDCO', "AttrType": 'DEBUG'},
                                            {"ParamName": 'D09', "AttrType": 'MON'}]}
        },
        {
            "EmbBlocks": {
                           {
                            "Block": [{
                                    {"BlockDef": {"BlockName": 'PIC400.IDFFA'}},
                                    {
                                        "Parameters": {"Parameter": [{"ParamName": 'ABCD', "ParamValue": 0},
                                        {"ParamName": 'EFGC', "ParamValue": 'ON'}]
                                        }
                                    },
                                    {
                                        "SymbolAttrs": {"SymbolAttr": [{"ParamName": 'PDCO', "AttrType": 'DEBUG'},
                                            {"ParamName": 'D09', "AttrType": 'MON'}]
                                        }
                                    },
                                    {
                                        "Connections": {"Connection":[{"InputEnd": "PIC400.ADF", "OutputEnd": "PIC300.CSQ"},
                                                                    {"InputEnd": "PIC400.ADF", "OutputEnd": "PIC100.ASD"}]

                                        }
                                    }
                                        
                                    }, {}, {}] # end of sub - Block (Each sub block has blockdef,parameters, symbolattrs, connections)

                           },
                           {"Block":[{}, {}]} # Each EmbBlocks will have Multiple sub-Block   
                            
                        } # End of EmbBlocks
        }
    ] # End of Main - Block
}