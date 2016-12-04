import cv2
import enum
import error
import numpy as np


class ImageObj():
    def __init__(self, image, code, contours=None):
        self.set(image, code, contours)

    def set(self, image, code, contours=None):
        self.image = image
        self.code = code
        self.contours = contours


class Canny():
    name = 'Canny'

    @staticmethod
    def get_image(obj, minval, maxval):
        image = cv2.Canny(obj.image, minval, maxval)
        return ImageObj(image, CvtColor.CvtCodes.GRAY, obj.contours)


class CvtColor():
    name = 'cvtColor'

    cvt_code_names = ['BGR', 'RGB', 'HSV', 'HLS', 'GRAY']
    CvtCodes = enum.IntEnum('Color', cvt_code_names)
    cvt_codes = \
        [[None, cv2.COLOR_BGR2RGB, cv2.COLOR_BGR2HSV,
         cv2.COLOR_BGR2HLS, cv2.COLOR_BGR2GRAY],
         [cv2.COLOR_RGB2BGR, None, cv2.COLOR_RGB2HSV,
          cv2.COLOR_RGB2HLS, cv2.COLOR_RGB2GRAY],
         [cv2.COLOR_HSV2BGR, cv2.COLOR_HSV2RGB, None, None, None],
         [cv2.COLOR_HLS2BGR, cv2.COLOR_HLS2RGB, None, None, None],
         [cv2.COLOR_GRAY2BGR, cv2.COLOR_GRAY2RGB, None, None, None]]

    @classmethod
    def get_image(cls, obj, code):
        cvt_code = cls.cvt_codes[obj.code-1][code-1]
        if cvt_code is None:
            return ImageObj(obj.image, obj.code, obj.contours)
        else:
            image = cv2.cvtColor(obj.image, cvt_code)
            return ImageObj(image, code, obj.contours)


class Thresh():
    name = 'threshold'

    thresh_type_names = \
        ['BINARY', 'BINARY_INV', 'TRUNC', 'TOZERO', 'TOZERO_INV']
    ThreshTypes = enum.IntEnum('Thresh', thresh_type_names)
    thresh_types = [cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV, cv2.THRESH_TRUNC,
                    cv2.THRESH_TOZERO, cv2.THRESH_TOZERO_INV]

    @classmethod
    def get_image(cls, img_obj, thresh, max_val, thresh_type):
        _, image = cv2.threshold(img_obj.image, thresh, max_val,
                                 cls.thresh_types[thresh_type-1])
        return ImageObj(image, img_obj.code, img_obj.contours)


class FindCnt():
    name = 'findContours'
    mode_names = ['LIST', 'EXTERNAL', 'CCOMP', 'TREE']
    Modes = enum.IntEnum('ContourMode', mode_names)
    modes = [cv2.RETR_LIST, cv2.RETR_EXTERNAL,
             cv2.RETR_CCOMP, cv2.RETR_TREE]

    method_names = ['NONE', 'SIMPLE', 'TC89_L1', 'TC89_KCOS']
    Methods = enum.IntEnum('ContourMethod', method_names)
    methods = [cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE,
               cv2.CHAIN_APPROX_TC89_L1, cv2.CHAIN_APPROX_TC89_KCOS]

    @classmethod
    def get_image(cls, obj, cnt_mode, cnt_method):
        if len(obj.image.shape) is not 2:
            raise error.ModuleError('input image should be one color only!')
        image = obj.image.copy()
        contours, hierarchy = \
            cv2.findContours(image,
                             cls.modes[cnt_mode-1],
                             cls.methods[cnt_method-1])
        return ImageObj(image, obj.code, contours)


class DrawCnt():
    name = 'drawContours'

    @staticmethod
    def get_image(obj_img, obj_cnt,
                  cnt_index=-1, color=(0, 255, 0), thickness=3):
        image = obj_img.image.copy()
        cv2.drawContours(image, obj_cnt.contours,
                         cnt_index, color, thickness)
        return ImageObj(image, obj_img.code, obj_cnt.contours)


class kNNnumber():
    name = 'kNNnumber'

    def __init__(self):
        train_color = cv2.imread('./digits.png')
        train_gray = cv2.cvtColor(train_color, cv2.COLOR_BGR2GRAY)
        train_cell = [np.hsplit(row, 100) for row in np.vsplit(train_gray, 50)]
        x = np.array(train_cell)
        train = x[:, :].reshape(-1, 400).astype(np.float32)
        k = np.arange(10)
        train_labels = np.repeat(k, 500)[:, np.newaxis]
        self.knn = cv2.KNearest()
        self.knn.train(train, train_labels)

    def get_image(self, obj, k):
        if len(obj.image.shape) is not 2:
                raise error.ModuleError('input image must be one color only!')
        test_gray = cv2.resize(obj.image, (20, 20))
        test = test_gray.reshape(-1, 400).astype(np.float32)
        ret, result, neighbours, dist = self.knn.find_nearest(test, k=5)
        image = obj.image.copy()
        cv2.rectangle(image, (0, 0), (100, 100), (0, 0, 0), -1)
        cv2.putText(image, str(int(result[0][0])), (0, 100),
                    cv2.FONT_HERSHEY_PLAIN, 8, (255, 255, 255))
        return ImageObj(image, obj.code, obj.contours)
