; Auto-generated. Do not edit!


(cl:in-package quori_interactions-msg)


;//! \htmlinclude ArmsCmd.msg.html

(cl:defclass <ArmsCmd> (roslisp-msg-protocol:ros-message)
  ((r_shoulder_pitch
    :reader r_shoulder_pitch
    :initarg :r_shoulder_pitch
    :type cl:float
    :initform 0.0)
   (r_shoulder_roll
    :reader r_shoulder_roll
    :initarg :r_shoulder_roll
    :type cl:float
    :initform 0.0)
   (l_shoulder_pitch
    :reader l_shoulder_pitch
    :initarg :l_shoulder_pitch
    :type cl:float
    :initform 0.0)
   (l_shoulder_roll
    :reader l_shoulder_roll
    :initarg :l_shoulder_roll
    :type cl:float
    :initform 0.0)
   (waist_pitch
    :reader waist_pitch
    :initarg :waist_pitch
    :type cl:float
    :initform 0.0))
)

(cl:defclass ArmsCmd (<ArmsCmd>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ArmsCmd>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ArmsCmd)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name quori_interactions-msg:<ArmsCmd> is deprecated: use quori_interactions-msg:ArmsCmd instead.")))

(cl:ensure-generic-function 'r_shoulder_pitch-val :lambda-list '(m))
(cl:defmethod r_shoulder_pitch-val ((m <ArmsCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_interactions-msg:r_shoulder_pitch-val is deprecated.  Use quori_interactions-msg:r_shoulder_pitch instead.")
  (r_shoulder_pitch m))

(cl:ensure-generic-function 'r_shoulder_roll-val :lambda-list '(m))
(cl:defmethod r_shoulder_roll-val ((m <ArmsCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_interactions-msg:r_shoulder_roll-val is deprecated.  Use quori_interactions-msg:r_shoulder_roll instead.")
  (r_shoulder_roll m))

(cl:ensure-generic-function 'l_shoulder_pitch-val :lambda-list '(m))
(cl:defmethod l_shoulder_pitch-val ((m <ArmsCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_interactions-msg:l_shoulder_pitch-val is deprecated.  Use quori_interactions-msg:l_shoulder_pitch instead.")
  (l_shoulder_pitch m))

(cl:ensure-generic-function 'l_shoulder_roll-val :lambda-list '(m))
(cl:defmethod l_shoulder_roll-val ((m <ArmsCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_interactions-msg:l_shoulder_roll-val is deprecated.  Use quori_interactions-msg:l_shoulder_roll instead.")
  (l_shoulder_roll m))

(cl:ensure-generic-function 'waist_pitch-val :lambda-list '(m))
(cl:defmethod waist_pitch-val ((m <ArmsCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader quori_interactions-msg:waist_pitch-val is deprecated.  Use quori_interactions-msg:waist_pitch instead.")
  (waist_pitch m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ArmsCmd>) ostream)
  "Serializes a message object of type '<ArmsCmd>"
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'r_shoulder_pitch))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'r_shoulder_roll))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'l_shoulder_pitch))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'l_shoulder_roll))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'waist_pitch))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ArmsCmd>) istream)
  "Deserializes a message object of type '<ArmsCmd>"
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'r_shoulder_pitch) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'r_shoulder_roll) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'l_shoulder_pitch) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'l_shoulder_roll) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'waist_pitch) (roslisp-utils:decode-single-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ArmsCmd>)))
  "Returns string type for a message object of type '<ArmsCmd>"
  "quori_interactions/ArmsCmd")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ArmsCmd)))
  "Returns string type for a message object of type 'ArmsCmd"
  "quori_interactions/ArmsCmd")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ArmsCmd>)))
  "Returns md5sum for a message object of type '<ArmsCmd>"
  "18963acf222a3961918de358f517947a")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ArmsCmd)))
  "Returns md5sum for a message object of type 'ArmsCmd"
  "18963acf222a3961918de358f517947a")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ArmsCmd>)))
  "Returns full string definition for message of type '<ArmsCmd>"
  (cl:format cl:nil "float32 r_shoulder_pitch~%float32 r_shoulder_roll~%float32 l_shoulder_pitch~%float32 l_shoulder_roll~%float32 waist_pitch~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ArmsCmd)))
  "Returns full string definition for message of type 'ArmsCmd"
  (cl:format cl:nil "float32 r_shoulder_pitch~%float32 r_shoulder_roll~%float32 l_shoulder_pitch~%float32 l_shoulder_roll~%float32 waist_pitch~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ArmsCmd>))
  (cl:+ 0
     4
     4
     4
     4
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ArmsCmd>))
  "Converts a ROS message object to a list"
  (cl:list 'ArmsCmd
    (cl:cons ':r_shoulder_pitch (r_shoulder_pitch msg))
    (cl:cons ':r_shoulder_roll (r_shoulder_roll msg))
    (cl:cons ':l_shoulder_pitch (l_shoulder_pitch msg))
    (cl:cons ':l_shoulder_roll (l_shoulder_roll msg))
    (cl:cons ':waist_pitch (waist_pitch msg))
))
