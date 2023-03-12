import torch
import torch.nn as nn
import SegNet_config as SegNet_cfg
#import segmentation_models.SegNet_config as SegNet_cfg

class SegNet(nn.Module):
    def __init__(self, n_layers, n_class=3, in_channels=3, is_unpooling=True, is_segmentation=False):
        super(SegNet, self).__init__()
        self.in_channels = in_channels
        self.is_unpooling = is_unpooling
        self.encoder, self.decoder, self.reconstructor = SegNet_cfg.get_SegNet(\
            SegNet_cfg.segnetLayerDict[n_layers], n_class)
        self.indices, self.shapes = [], []
        self.segmentation = is_segmentation
        self.softmax = nn.Softmax(dim=1)
    
    def set_index(self, indices, shapes):
        self.indices, self.shapes = indices,shapes
            

    def encode(self, inputs):
        self.indices, self.shapes = [], []
        for idx in range(len(self.encoder)):
            inputs, indices, shapes = self.encoder[idx](inputs)
            self.indices.append(indices)
            self.shapes.append(shapes)
        self.shapes.reverse()
        self.indices.reverse()
        return inputs
    
    def decode(self, inputs):
        for idx in range(len(self.decoder)):
            inputs = self.decoder[idx](inputs, indices=self.indices[idx], shapes=self.shapes[idx])
        
        if self.segmentation:
            inputs = self.softmax(inputs)
        return inputs
    
    def forward(self, inputs):
        out = self.encode(inputs)
        out = self.decode(out)
        return out
    
    def reconstruct(self, inputs):
        for idx in range(len(self.reconstructor)):
            inputs = self.reconstructor[idx](inputs, indices=self.indices[idx], shapes=self.shapes[idx]) 
        return inputs

if __name__ == '__main__':
    model = SegNet(n_layers=13, n_class=3)
    print(model)
    x = torch.rand(1, 3, 360, 480)
    out = model(x)
    print(out.shape)
