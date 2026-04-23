; Auto-generated. Do not edit!


(cl:in-package quori_gui-msg)


;//! \htmlinclude Opcmd.msg.html

(cl:defclass <Opcmd> (roslisp-msg-protocol:ros-message)
  ((data
    :reader data
    :initarg :data
    :type cl:string
    :initform "")
   (angle_dist
    :reader angle_dist
    :initarg :angle_dist
    :type cl:float
    :initform 0.0))
)

(cl:defclass Opcmd (<Opcmd>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Opcmd>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Opcmd)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name quori_gui-msg:<Opcmd> is deprecated: use quori_gui-msg:Opcmd instead.")))

(cl:ensure-generic-function 'data-val :lambda-list '(m))
(cl:defmethod data-val ((m <Opcmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_gui-msg:data-val is deprecated.  Use quori_gui-msg:data instead.")
  (data m))

(cl:ensure-generic-function 'angle_dist-val :lambda-list '(m))
(cl:defmethod angle_dist-val ((m <Opcmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_gui-msg:angle_dist-val is deprecated.  Use quori_gui-msg:angle_dist instead.")
  (angle_dist m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Opcmd>) ostream)
  "Serializes a message object of type '<Opcmd>"
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'data))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'data))
  (cl:let ((bits (roslisp-utils:encode-double-float-bits (cl:slot-value msg 'angle_dist))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Opcmd>) istream)
  "Deserializes a message object of type '<Opcmd>"
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'data) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'data) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'angle_dist) (roslisp-utils:decode-double-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Opcmd>)))
  "Returns string type for a message object of type '<Opcmd>"
  "quori_gui/Opcmd")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Opcmd)))
  "Returns string type for a message object of type 'Opcmd"
  "quori_gui/Opcmd")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Opcmd>)))
  "Returns md5sum for a message object of type '<Opcmd>"
  "8e95fd03b16cd7241921e03a50a02cad")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Opcmd)))
  "Returns md5sum for a message object of type 'Opcmd"
  "8e95fd03b16cd7241921e03a50a02cad")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Opcmd>)))
  "Returns full string definition for message of type '<Opcmd>"
  (cl:format cl:nil "string data~%float64 angle_dist~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Opcmd)))
  "Returns full string definition for message of type 'Opcmd"
  (cl:format cl:nil "string data~%float64 angle_dist~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Opcmd>))
  (cl:+ 0
     4 (cl:length (cl:slot-value msg 'data))
     8
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Opcmd>))
  "Converts a ROS message object to a list"
  (cl:list 'Opcmd
    (cl:cons ':data (data msg))
    (cl:cons ':angle_dist (angle_dist msg))
))
