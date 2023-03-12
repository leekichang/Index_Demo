import torch.nn as nn

'''
segnetLayerDict
keys(int) -> Number of conv-bn-relu block,
values(list) -> Channel information, len(values)-1 == number of block
e.g. key:2, value:[3, 64, 128]
means that there are 2 conv-bn-relu per a block, 2 blocks(len(value)-1 == 2)
first block channel 3->64
second block channel 64->128
'''
segnetLayerDict={8:{2:[3, 64, 128, 256, 512]},
                 10:{2:[3, 64, 128, 256, 512, 512]},
                 13:{2:[3, 64, 128], 3:[128, 256, 512, 512]},
                 16:{2:[3, 64, 128], 4:[128, 256, 512, 512]}}

class Conv2DBatchNormRelu(nn.Module):
    def __init__(self, in_channels, n_filters, kernel_size=3,\
                 stride=1, padding=1, bias=True, dilation=1, with_bn=True):
        super(Conv2DBatchNormRelu, self).__init__()
        conv_mod = nn.Conv2d(int(in_channels), int(n_filters), kernel_size=kernel_size,\
                             padding=padding, stride=stride, bias=bias, dilation=dilation, )
        if with_bn:
            self.cbr_unit = nn.Sequential(conv_mod, nn.BatchNorm2d(int(n_filters)), nn.ReLU(inplace=True))
        else:
            self.cbr_unit = nn.Sequential(conv_mod, nn.ReLU(inplace=True))
    
    def forward(self, inputs):
        output = self.cbr_unit(inputs)
        return output

class SegnetEnc(nn.Module):
    def __init__(self, in_channel, out_channel, n_layers, is_unpool=True):
        super(SegnetEnc, self).__init__()
        self.n_layers = n_layers
        self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2, return_indices=is_unpool)
        #self.convs = nn.Sequential(Conv2DBatchNormRelu(in_channels=in_channel, n_filters=out_channel))
        modules = [Conv2DBatchNormRelu(in_channels=in_channel, n_filters=out_channel)]

        for layer in range(1, self.n_layers):
            modules.append(Conv2DBatchNormRelu(in_channels=out_channel, n_filters=out_channel))
        self.convs = nn.Sequential(*modules)
        
    def forward(self, inputs):
        output = self.convs(inputs)
        shapes = output.shape
        output, indices = self.maxpool(output)
        return output, indices, shapes

class SegnetDec(nn.Module):
    def __init__(self, in_channel, out_channel, n_layers, kernel_size=3):
        super(SegnetDec, self).__init__()
        self.unpool = nn.MaxUnpool2d(2, 2)
        self.n_layers = n_layers
        # self.convs = nn.Sequential()
        modules = []
        for idx in range(self.n_layers-1):
            modules.append(Conv2DBatchNormRelu(in_channels=in_channel, n_filters=in_channel))
        modules.append(Conv2DBatchNormRelu(in_channels=in_channel, n_filters=out_channel))
        self.convs = nn.Sequential(*modules)
        
    def forward(self, inputs, indices, shapes):
        outputs = self.unpool(input=inputs, indices=indices, output_size=shapes)
        outputs = self.convs(outputs)
        return outputs

class UpSampleDec(SegnetDec):
    '''
    Class for upsample decoder test
    '''
    def __init__(self, in_channel, out_channel, n_layers):
        super(UpSampleDec, self).__init__(in_channel, out_channel, n_layers)
        self.unpool = nn.Upsample(scale_factor=2)
                
    def forward(self, inputs):
        outputs = self.unpool(inputs)
        outputs = self.convs(outputs)
        return outputs

def get_SegNet(layer_dict, n_class):
    encoders, decoders, reconsts = [], [], []
    for jdx, key in enumerate(layer_dict.keys()):
        for idx in range(len(layer_dict[key])-1):
            encoders.append(SegnetEnc(in_channel=layer_dict[key][idx],
                                      out_channel=layer_dict[key][idx+1],
                                      n_layers=key))
            if idx == 0 and jdx == 0 and n_class != layer_dict[key][0]:
                decoders.append(SegnetDec(in_channel=layer_dict[key][idx+1],
                                        out_channel=n_class,
                                        n_layers=key))
            else:
                decoders.append(SegnetDec(in_channel=layer_dict[key][idx+1],
                                        out_channel=layer_dict[key][idx],
                                        n_layers=key))
            reconsts.append(SegnetDec(in_channel=layer_dict[key][idx+1],
                                    out_channel=layer_dict[key][idx],
                                    n_layers=key))
    decoders.reverse()
    reconsts.reverse()
    return nn.ModuleList(encoders), nn.ModuleList(decoders), nn.ModuleList(reconsts)

if __name__ == '__main__':
    model = get_SegNet(segnetLayerDict[8], 3)
    print(model)

